import boto3

class AWSCredentialManager:
    def __init__(self, access_key_id=None, secret_access_key=None, session_token=None, region=None):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.session_token = session_token
        self.region = region

    def create_session(self, region_name=None):
        return boto3.Session(
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            aws_session_token=self.session_token,
            region_name=region_name or self.region
        )

# Global instance for easy access
aws_credentials = AWSCredentialManager()