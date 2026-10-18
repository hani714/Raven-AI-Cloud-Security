import hmac
import hashlib
import logging
from typing import Optional

from paddle_billing import Client, Environment, Options
from paddle_billing.Exceptions.ApiError import ApiError
from paddle_billing.Resources.Customers.Operations import CreateCustomer, ListCustomers
from paddle_billing.Resources.Transactions.Operations import CreateTransaction
from paddle_billing.Resources.Transactions.Operations.Create import TransactionCreateItem

from app.utils import settings


logger = logging.getLogger(__name__)

class PaddlePayment:
    def __init__(self):
        self.environment = (
            Environment.SANDBOX
            if settings.PADDLE_API_KEY.startswith("pdl_sdbx_")
            else Environment.PRODUCTION
        )
        self.paddle_client = Client(
            settings.PADDLE_API_KEY,
            options=Options(self.environment)
        )

    @property
    def environment_name(self) -> str:
        return "sandbox" if self.environment == Environment.SANDBOX else "production"

    @staticmethod
    def verify_paddle_signature(raw_body: bytes, signature: str):
        signature_parts = {}
        for item in signature.split(";"):
            if "=" not in item:
                continue
            key, value = item.split("=", 1)
            key = key.strip().lower()
            value = value.strip()

            if key == "h1":
                signature_parts.setdefault("h1", []).append(value)
            else:
                signature_parts[key] = value

        ts = signature_parts.get("ts")
        signatures = signature_parts.get("h1", [])

        # Backward-compatibility fallback for non-standard header values.
        if not ts or not signatures:
            computed = hmac.new(
                settings.PADDLE_WEBHOOK_SECRET.encode("utf-8"),
                raw_body,
                hashlib.sha256,
            ).hexdigest()
            return hmac.compare_digest(computed, signature.strip())

        try:
            raw_body_text = raw_body.decode("utf-8")
        except UnicodeDecodeError:
            return False

        signed_payload = f"{ts}:{raw_body_text}".encode("utf-8")
        computed = hmac.new(
            settings.PADDLE_WEBHOOK_SECRET.encode("utf-8"),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()

        return any(hmac.compare_digest(computed, expected) for expected in signatures)

    def list_products(self):
        try:
            products = self.paddle_client.prices.list()
            for product in products:
                print(f"Product's id: {product.id}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Paddle client: {str(e)}")

    def assert_price_exists(self, price_id: str) -> None:
        try:
            price = self.paddle_client.prices.get(price_id)
            if price is None or getattr(price, "id", None) != price_id:
                raise RuntimeError(f"Paddle price_id not found: {price_id}")
        except ApiError as e:
            raise RuntimeError(f"Failed to validate Paddle price_id {price_id}: {e.detail}")
        except Exception as e:
            raise RuntimeError(f"Failed to validate Paddle price_id {price_id}: {str(e)}")

    def _get_or_create_customer_id(self, customer_email: str) -> str:
        customers = self.paddle_client.customers.list(ListCustomers(emails=[customer_email]))
        existing_customer = next(iter(customers), None)

        if existing_customer:
            return existing_customer.id

        created_customer = self.paddle_client.customers.create(CreateCustomer(email=customer_email))
        return created_customer.id
    
    async def create_transaction(
        self,
        price_id: str,
        customer_email: Optional[str] = None,
        quantity: int = 1,
    ):
        try:
            operation = CreateTransaction(items=[TransactionCreateItem(price_id=price_id, quantity=quantity)])

            if customer_email:
                operation.customer_id = self._get_or_create_customer_id(customer_email)

            transaction = self.paddle_client.transactions.create(operation)

            if transaction.checkout is None or not transaction.checkout.url:
                raise RuntimeError(
                    f"Transaction created without checkout URL (transaction_id={transaction.id}, status={transaction.status})"
                )

            return {
                "transaction_id": transaction.id,
                "checkout_url": transaction.checkout.url,
            }
        except ApiError as e:
            field_errors = [
                {"field": fe.field, "message": fe.error}
                for fe in e.field_errors
            ]
            logger.error(
                "Paddle transaction validation failed",
                extra={
                    "extra_data": {
                        "error_type": e.error_type,
                        "error_code": e.error_code,
                        "detail": e.detail,
                        "field_errors": field_errors,
                        "docs_url": e.docs_url,
                        "price_id": price_id,
                        "quantity": quantity,
                        "has_customer_email": bool(customer_email),
                    }
                },
            )
            if field_errors:
                first = field_errors[0]
                raise RuntimeError(
                    f"Failed to create Paddle transaction: {e.detail} ({first['field']}: {first['message']})"
                )
            raise RuntimeError(f"Failed to create Paddle transaction: {e.detail}")
        except Exception as e:
            logger.error("Error creating Paddle transaction: %s", str(e))
            raise RuntimeError(f"Failed to create Paddle transaction: {str(e)}")