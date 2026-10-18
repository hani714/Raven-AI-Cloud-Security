from fastapi import APIRouter, HTTPException

from app.utils.dependency import CurrentUser, ScanService, Redis
from app.schemas import ScanCreate, ScanResponse, ScanResultResponse

router = APIRouter(prefix="/scans", tags=["Scans"])

# Get all scans
@router.get("/", response_model=list[ScanResponse])
async def get_scans(
    current_user: CurrentUser,
    service: ScanService
):
    try:
        return await service.get_scans_by_user(current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a new scan
@router.post("/", response_model=ScanResponse)
async def create_scan(
    scan: ScanCreate,
    current_user: CurrentUser,
    service: ScanService
):
    try:
        result = await service.create_scan(scan, current_user)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Scan results
@router.get("/{scan_id}/results", response_model=ScanResultResponse)
async def get_scan_results(
    scan_id: str,
    current_user: CurrentUser,
    cache: Redis,
    service: ScanService
):
    try:
        return await service.get_scan_results(scan_id, current_user.id, cache)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
