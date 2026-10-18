from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


class ByokRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_keys_by_user(self, user_id: str):
        result = await self.db.execute(
            select(models.UserApiKeys)
            .options(
                selectinload(models.UserApiKeys.provider),
                selectinload(models.UserApiKeys.model),
            )
            .where(models.UserApiKeys.user_id == user_id)
        )
        return result.scalars().all()

    async def get_key_by_id(self, key_id: str):
        result = await self.db.execute(
            select(models.UserApiKeys)
            .options(
                selectinload(models.UserApiKeys.provider),
                selectinload(models.UserApiKeys.model),
            )
            .where(models.UserApiKeys.id == key_id)
        )
        return result.scalar_one_or_none()

    async def get_user_key_for_model(self, user_id: str, model_id: str):
        result = await self.db.execute(
            select(models.UserApiKeys)
            .options(
                selectinload(models.UserApiKeys.provider),
                selectinload(models.UserApiKeys.model),
            )
            .where(
                models.UserApiKeys.user_id == user_id,
                models.UserApiKeys.model_id == model_id,
            )
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_provider_by_slug(self, slug: str):
        result = await self.db.execute(
            select(models.Providers)
            .where(
                models.Providers.slug == slug,
                models.Providers.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    async def get_provider_by_slug_any(self, slug: str):
        result = await self.db.execute(
            select(models.Providers)
            .where(models.Providers.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_provider_model(self, provider_id: str, model_id: str):
        result = await self.db.execute(
            select(models.ProviderModels)
            .where(
                models.ProviderModels.provider_id == provider_id,
                models.ProviderModels.model_id == model_id,
                models.ProviderModels.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    async def get_provider_model_any(self, provider_id: str, model_id: str):
        result = await self.db.execute(
            select(models.ProviderModels)
            .where(
                models.ProviderModels.provider_id == provider_id,
                models.ProviderModels.model_id == model_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_models_by_provider_slug(self, slug: str):
        result = await self.db.execute(
            select(models.ProviderModels)
            .join(models.Providers, models.ProviderModels.provider_id == models.Providers.id)
            .where(
                models.Providers.slug == slug,
                models.Providers.is_active == True,
                models.ProviderModels.is_active == True,
            )
            .order_by(models.ProviderModels.display_name.asc(), models.ProviderModels.model_id.asc())
        )
        return result.scalars().all()

    async def create_key(self, key: models.UserApiKeys):
        self.db.add(key)
        await self.db.commit()
        await self.db.refresh(key)
        return key

    async def delete_key(self, key: models.UserApiKeys):
        await self.db.delete(key)
        await self.db.commit()
        return key

    async def seed_providers_and_models(self, provider_payload: list[dict]) -> dict:
        created_providers = 0
        updated_providers = 0
        created_models = 0
        updated_models = 0

        for provider_data in provider_payload:
            slug = provider_data["slug"]
            display_name = provider_data["display_name"]

            provider = await self.get_provider_by_slug_any(slug)
            if provider:
                changed = False
                if provider.display_name != display_name:
                    provider.display_name = display_name
                    changed = True
                if provider.is_active is not True:
                    provider.is_active = True
                    changed = True
                if changed:
                    updated_providers += 1
            else:
                provider = models.Providers(
                    slug=slug,
                    display_name=display_name,
                    is_active=True,
                )
                self.db.add(provider)
                await self.db.flush()
                created_providers += 1

            for model_data in provider_data.get("models", []):
                model_id = model_data["model_id"]
                model_display = model_data["display_name"]

                existing = await self.get_provider_model_any(provider.id, model_id)
                if existing:
                    changed = False
                    if existing.display_name != model_display:
                        existing.display_name = model_display
                        changed = True
                    if existing.is_active is not True:
                        existing.is_active = True
                        changed = True
                    if changed:
                        updated_models += 1
                    continue

                self.db.add(
                    models.ProviderModels(
                        provider_id=provider.id,
                        model_id=model_id,
                        display_name=model_display,
                        is_active=True,
                    )
                )
                created_models += 1

        await self.db.commit()

        return {
            "providers_created": created_providers,
            "providers_updated": updated_providers,
            "models_created": created_models,
            "models_updated": updated_models,
        }

    async def clear_providers_and_models(self) -> dict:
        keys_result = await self.db.execute(delete(models.UserApiKeys))
        models_result = await self.db.execute(delete(models.ProviderModels))
        providers_result = await self.db.execute(delete(models.Providers))
        await self.db.commit()

        return {
            "user_api_keys": keys_result.rowcount or 0,
            "provider_models": models_result.rowcount or 0,
            "providers": providers_result.rowcount or 0,
        }

    async def get_active_providers(self):
        result = await self.db.execute(
            select(models.Providers)
            .options(selectinload(models.Providers.models))
            .where(models.Providers.is_active == True)
            .order_by(models.Providers.display_name.asc())
        )
        return result.scalars().all()
