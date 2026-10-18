from fastapi import APIRouter, status

from app.schemas import ByokKeyCreate, ByokKeyResponse, ByokProviderOption, ByokProviderModelOption
from app.utils.dependency import CurrentUser, BYOKService

router = APIRouter(prefix="/byok", tags=["BYOK"])


@router.get("/keys", response_model=list[ByokKeyResponse])
async def get_keys(
	current_user: CurrentUser,
	service: BYOKService,
):
	return await service.get_keys_by_user(current_user.id)


@router.get("/providers", response_model=list[ByokProviderOption])
async def get_providers(
	service: BYOKService,
):
	return await service.get_providers()


@router.get("/providers/{provider_slug}/models", response_model=list[ByokProviderModelOption])
async def get_provider_models(
	provider_slug: str,
	service: BYOKService,
):
	return await service.get_provider_models(provider_slug)


@router.post("/providers/seed", status_code=status.HTTP_200_OK)
async def seed_providers(
	service: BYOKService,
):
	return await service.seed_providers_and_models()

@router.delete("/providers/clear", status_code=status.HTTP_200_OK)
async def clear_providers(
	service: BYOKService,
):
	return await service.clear_providers_and_models()


@router.post("/keys", response_model=ByokKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_key(
	payload: ByokKeyCreate,
	current_user: CurrentUser,
	service: BYOKService,
):
	return await service.create_key(payload, current_user)


@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_key(
	key_id: str,
	current_user: CurrentUser,
	service: BYOKService,
):
	return await service.delete_key(key_id, current_user)

