import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iam_enumeration import get_iam_data
from app.modules.s3_enumeration import get_s3_data
from app.modules.lambda_enumeration import get_lambda_data
from credentials import AWSCredentialManager

logger = logging.getLogger(__name__)

class Enumerator:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_enumeration(self, scan_id: str, environment):

        session = AWSCredentialManager(
            access_key_id=environment.access_key,
            secret_access_key=environment.secret_access_key,
            region=environment.region
        ).create_session()

        try:
            iam_data, s3_data, lambda_data = await asyncio.gather(
                get_iam_data(scan_id, session=session),
                get_s3_data(scan_id, session=session),
                get_lambda_data(scan_id, session=session),
            )

        except Exception as e:
            raise RuntimeError(f"Enumeration failed: {str(e)}")

        return {
            "iam": iam_data,
            "s3": s3_data,
            "lambda": lambda_data
        }