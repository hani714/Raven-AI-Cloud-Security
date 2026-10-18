import logging
from fastapi import HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.repositories import UserRepository, ByokRepository
from app.utils import build_provider_seed, fetch_litellm_models, encrypt_api_key

logger = logging.getLogger(__name__)

class BYOKService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.byok_repo = ByokRepository(db)

    async def get_keys_by_user(self, user_id: str):
        keys = await self.byok_repo.get_keys_by_user(user_id)
        return [self._to_response(key) for key in keys]

    async def create_key(self, payload: schemas.ByokKeyCreate, current_user: schemas.CurrentUser):
        user = await self.user_repo.get_user(current_user.id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        provider = await self.byok_repo.get_provider_by_slug(payload.provider)
        if not provider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found.")

        model = await self.byok_repo.get_provider_model(provider.id, payload.model)
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found.")

        new_key = models.UserApiKeys(
            user_id=user.id,
            provider_id=provider.id,
            model_id=model.id,
            label=payload.label,
            encrypted_key=encrypt_api_key(payload.api_key),
            key_preview=self._key_preview(payload.api_key),
        )

        created = await self.byok_repo.create_key(new_key)
        created.provider = provider
        created.model = model
        return self._to_response(created)

    async def delete_key(self, key_id: str, current_user: schemas.CurrentUser):
        key = await self.byok_repo.get_key_by_id(key_id)
        if not key or str(key.user_id) != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found.")

        await self.byok_repo.delete_key(key)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    async def get_providers(self):
        providers = await self.byok_repo.get_active_providers()
        response: list[schemas.ByokProviderOption] = []

        for provider in providers:
            active_models = [m for m in (provider.models or []) if m.is_active]
            default_model = ""
            if active_models:
                active_models.sort(key=lambda m: (m.display_name or "", m.model_id))
                default_model = active_models[0].model_id

            response.append(
                schemas.ByokProviderOption(
                    value=provider.slug,
                    label=provider.display_name,
                    default_model=default_model,
                )
            )

        return response

    async def get_provider_models(self, provider_slug: str):
        provider = await self.byok_repo.get_provider_by_slug(provider_slug)
        if not provider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found.")

        models = await self.byok_repo.get_models_by_provider_slug(provider_slug)
        response: list[schemas.ByokProviderModelOption] = []

        default_model_id = models[0].model_id if models else None
        for model in models:
            response.append(
                schemas.ByokProviderModelOption(
                    value=model.model_id,
                    label=model.display_name,
                    is_default=bool(default_model_id and model.model_id == default_model_id),
                )
            )

        return response

    def _to_response(self, key: models.UserApiKeys) -> schemas.ByokKeyResponse:
        return schemas.ByokKeyResponse(
            id=key.id,
            provider=key.provider.slug if key.provider else "",
            model=key.model.model_id if key.model else "",
            model_id=key.model.id if key.model else None,
            label=key.label,
            key_preview=key.key_preview,
            created_at=getattr(key, "created_at", None),
        )

    def _key_preview(self, api_key: str) -> str:
        trimmed = api_key.strip()
        return trimmed[-4:] if len(trimmed) >= 4 else trimmed

    async def seed_providers_and_models(self) -> dict:
        model_catalog = await fetch_litellm_models()
        provider_payload = build_provider_seed(model_catalog)
        return await self.byok_repo.seed_providers_and_models(provider_payload)

    async def clear_providers_and_models(self) -> dict:
        return await self.byok_repo.clear_providers_and_models()