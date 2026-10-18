import aioboto3

from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError

from credentials import AWSCredentialManager


class STS:
    def __init__(self, aws_credentials: AWSCredentialManager):
        self.session = aws_credentials.create_session()
        creds = self.session.get_credentials()
        frozen_creds = creds.get_frozen_credentials() if creds else None
        self.aiosession = aioboto3.Session(
            aws_access_key_id=frozen_creds.access_key if frozen_creds else None,
            aws_secret_access_key=frozen_creds.secret_key if frozen_creds else None,
            aws_session_token=frozen_creds.token if frozen_creds else None,
            region_name=self.session.region_name,
        )

    async def get_caller_identity(self):
        try:
            async with self.aiosession.client("sts") as sts_client:
                return await sts_client.get_caller_identity()
        except NoCredentialsError:
            raise RuntimeError("AWS credentials not found")
        except EndpointConnectionError:
            raise RuntimeError("Cannot reach AWS STS endpoint")
        except ClientError as e:
            raise RuntimeError(f"AWS STS error: {e.response['Error']['Code']}")