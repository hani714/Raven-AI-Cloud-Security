from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class S3Object:
    key: str
    size: int
    last_modified: Optional[str] = None
    etag: Optional[str] = None
    storage_class: Optional[str] = None
    acl: Dict[str, Any] = field(default_factory=dict)
    tags: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version_id: Optional[str] = None


@dataclass
class S3Bucket:
    name: str
    scan_id: str
    creation_date: Optional[str] = None
    region: Optional[str] = None
    
    # Bucket configurations
    acl: Dict[str, Any] = field(default_factory=dict)
    policy: Dict[str, Any] = field(default_factory=dict)
    policy_status: Dict[str, Any] = field(default_factory=dict)
    public_access_block: Dict[str, Any] = field(default_factory=dict)
    website_config: Dict[str, Any] = field(default_factory=dict)
    cors_config: Dict[str, Any] = field(default_factory=dict)
    encryption_config: Dict[str, Any] = field(default_factory=dict)
    versioning_config: Dict[str, Any] = field(default_factory=dict)
    replication_config: Dict[str, Any] = field(default_factory=dict)
    logging_config: Dict[str, Any] = field(default_factory=dict)
    lifecycle_config: Dict[str, Any] = field(default_factory=dict)
    notification_config: Dict[str, Any] = field(default_factory=dict)
    tagging: List[Dict[str, str]] = field(default_factory=list)
    
    # Object information
    objects: List[S3Object] = field(default_factory=list)
    object_count: int = 0
    total_size: int = 0


@dataclass
class S3EnumerationResult:
    account_id: str
    current_user: Optional[str]
    buckets: List[S3Bucket]
    enumeration_time: str
    total_buckets: int = 0
    total_objects: int = 0
    total_size: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)
    permissions_checked: List[str] = field(default_factory=list)
