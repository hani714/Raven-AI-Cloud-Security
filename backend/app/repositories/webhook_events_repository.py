from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WebhookEvent


class WebhookEventsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_provider_event_id(self, provider_event_id: str) -> WebhookEvent | None:
        result = await self.db.execute(
            select(WebhookEvent).where(WebhookEvent.provider_event_id == provider_event_id)
        )
        return result.scalar_one_or_none()

    async def create_event(
        self,
        provider_event_id: str,
        event_type: str,
        payload_json: dict,
        provider: str = "paddle",
    ) -> WebhookEvent:
        event = WebhookEvent(
            provider=provider,
            provider_event_id=provider_event_id,
            event_type=event_type,
            payload_json=payload_json,
            processing_status="RECEIVED",
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def set_status(
        self,
        event: WebhookEvent,
        status: str,
        processing_error: str | None = None,
    ) -> WebhookEvent:
        event.processing_status = status
        event.processing_error = processing_error
        event.processed_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(event)
        return event
