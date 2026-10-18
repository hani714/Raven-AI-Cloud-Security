from fastapi import APIRouter, status

from app.schemas import EnvironmentResponse, EnvironmentCreate
from app.utils.dependency import CurrentUser, EnvService

router = APIRouter(prefix="/environments", tags=["Environments"])

# Get all environments
@router.get("/", response_model=list[EnvironmentResponse])
async def get_environments(
    current_user: CurrentUser,
    service: EnvService
):
    return await service.get_environments_by_user(current_user.id)


# Create a new environment
@router.post("/", response_model=EnvironmentResponse)
async def create_environment(
    environment: EnvironmentCreate,
    current_user: CurrentUser,
    service: EnvService
):
    return await service.create_environment(environment.to_dto(), current_user)


# Delete an environment
@router.delete("/{environment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_environment(
    environment_id: str,
    current_user: CurrentUser,
    service: EnvService
):
    return await service.delete_environment(environment_id, current_user)


# Test connection to an environment
@router.post("/{environment_id}/test-connection")
async def test_environment_connection(
    environment_id: str,
    current_user: CurrentUser,
    service: EnvService
):
    return await service.test_environment_connection(environment_id, current_user)