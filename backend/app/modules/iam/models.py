from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class IAMUser:
    username: str
    user_id: str
    arn: str
    path: str
    create_date: str
    scan_id: str
    managed_policies: List[Dict[str, Any]]
    inline_policies: List[Dict[str, Any]]
    groups: List[str]
    tags: List[Dict[str, str]]
    access_keys: List[Dict[str, Any]]


@dataclass
class IAMRole:
    role_name: str
    role_id: str
    arn: str
    path: str
    create_date: str
    scan_id: str
    assume_role_policy: Dict[str, Any]
    managed_policies: List[Dict[str, Any]]
    inline_policies: List[Dict[str, Any]]
    tags: List[Dict[str, str]]


@dataclass
class IAMGroup:
    group_name: str
    group_id: str
    arn: str
    path: str
    create_date: str
    scan_id: str
    managed_policies: List[Dict[str, Any]]
    inline_policies: List[Dict[str, Any]]
    members: List[str]


@dataclass
class IAMEnumerationResult:
    current_user: Optional[str]
    users: List[IAMUser]
    roles: List[IAMRole]
    groups: List[IAMGroup]
    enumeration_time: str
    errors: List[Dict[str, str]]
    permissions_checked: List[str]


@dataclass
class IAMControlFinding:
    scan_id: str
    control_id: str
    title: str
    severity: str
    status: str
    resource_type: str
    resource_id: str
    reason: str
    evidence: Dict[str, Any]
    created_at: Optional[str] = None