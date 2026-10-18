from fastapi import APIRouter, HTTPException

from app.utils.dependency import CurrentUser, GenAIService, Redis

router = APIRouter(prefix="/genai", tags=["GenAI"])

# Get all scans
@router.get("/{scan_id}", response_model=None)
async def get_attack_path(
    scan_id: str,
    cache: Redis,
    current_user: CurrentUser,
    service: GenAIService
):
    result = await service.get_attack_path(scan_id, current_user.id, cache)
    if result is None:
        raise HTTPException(status_code=404, detail="No scan results found")
    return result