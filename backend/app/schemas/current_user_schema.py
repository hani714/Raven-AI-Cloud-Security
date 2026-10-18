from uuid import UUID
from dataclasses import dataclass

from app.models.enums import ScanDepth, AnalysisLevel

@dataclass(frozen=True)
class CurrentUser():
    id: UUID
    email: str
    subscription_id: str
    subscription_name: str
    scan_depth: ScanDepth
    analysis_level: AnalysisLevel
    max_environments: int
    max_scans_per_month: int


@dataclass(frozen=True)
class UserActivity():
    current_environments: int
    current_scans_per_month: int
    max_environments: int
    max_scans_per_month: int
    analysis_level: AnalysisLevel