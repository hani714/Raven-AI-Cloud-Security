import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import Response
from fastapi import HTTPException, status

from app.modules.sts import STS
from app import schemas, models
from app.dto import EnvironmentCreateDTO
from credentials import AWSCredentialManager
from app.repositories import EnvironmentRepository, UserRepository, SubscriptionsRepository

logger = logging.getLogger(__name__)

class EnvironmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.subs_repo = SubscriptionsRepository(db)
        self.env_repo = EnvironmentRepository(db)
        self.user_repo = UserRepository(db)
        
    # Get scans by user ID
    async def get_environments_by_user(self, user_id: str):
        return await self.env_repo.get_by_user(user_id)

    # Create a new environment
    async def create_environment(self, environment_data: EnvironmentCreateDTO, current_user: schemas.CurrentUser):
        user = await self.user_repo.get_user(current_user.id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        
        sub = await self.subs_repo.get_subscription_by_user(current_user.id)
        if sub.current_environments >= current_user.max_environments:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Environment limit reached for the current subscription."
            )
        
        new_environment = models.Environments(
            name=environment_data.name,
            access_key=environment_data.access_key,
            secret_access_key=environment_data.secret_access_key,
            region=environment_data.region,
            user_id=user.id,
        )
        
        return await self.env_repo.create(new_environment, sub)
    
    # Delete an environment
    async def delete_environment(self, environment_id: str, current_user: schemas.CurrentUser):
        environment = await self.env_repo.get_by_id(environment_id)
        
        if not environment or str(environment.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found."
            )
        
        sub = await self.subs_repo.get_subscription_by_user(current_user.id)
        await self.env_repo.delete(environment, sub)
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    # Test connection to an environment
    async def test_environment_connection(self, environment_id: str, current_user: schemas.CurrentUser):
        environment = await self.env_repo.get_by_id(environment_id)
        
        if not environment or str(environment.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found."
            )
        
        try:
            credential_manager = AWSCredentialManager(
                access_key_id=environment.access_key,
                secret_access_key=environment.secret_access_key,
                region=environment.region
            )

            sts = STS(credential_manager)
            result = await sts.get_caller_identity()

            return {"is_valid": True, "message": "Connection successful."}
        except RuntimeError as e:
            return {"is_valid": False, "message": str(e)}
        except Exception as e:
            return {"is_valid": False, "message": f"Unexpected error: {str(e)}"}