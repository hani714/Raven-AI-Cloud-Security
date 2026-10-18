import asyncio
import logging

import resend
from brevo import AsyncBrevo
from brevo.transactional_emails import (
    SendTransacEmailRequestSender,
    SendTransacEmailRequestToItem,
)

from app.utils import settings
from app.dto.email_dto import EmailDTO

logger = logging.getLogger(__name__)

class EmailService:

    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY
        self.brevo_client = AsyncBrevo(api_key=settings.BREVO_API_KEY)

    async def send_email_resend(self, email_dto: EmailDTO):
        try:
            response = await asyncio.to_thread(resend.Emails.send, {
                "from": "onboarding@resend.dev",
                "to": email_dto.to,
                "subject": email_dto.subject,
                "html": email_dto.html,
            })
            return response

        except Exception as e:
            logger.error(f"Error sending email via Resend: {e}")
            return None

    async def send_email_brevo(self, email_dto: EmailDTO):
        try:
            response = await self.brevo_client.transactional_emails.send_transac_email(
                subject=email_dto.subject,
                html_content=email_dto.html,
                sender=SendTransacEmailRequestSender(
                    name="RAVEN",
                    email="noreply@shoukan-labs.com",
                ),
                to=[
                    SendTransacEmailRequestToItem(
                        email=email_dto.to,
                    )
                ]
            )
            return response

        except Exception as e:
            logger.error(f"Error sending email via Brevo: {e}")
            return None