from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class LambdaFunction:
    # Basic function information
    function_name: str
    function_arn: str
    scan_id: str
    runtime: Optional[str] = None
    role: Optional[str] = None
    handler: Optional[str] = None
    code_size: Optional[int] = None
    description: Optional[str] = None
    timeout: Optional[int] = None
    memory_size: Optional[int] = None
    last_modified: Optional[str] = None
    code_sha256: Optional[str] = None
    version: Optional[str] = None
    
    # Environment and configuration
    environment: Dict[str, Any] = field(default_factory=dict)
    dead_letter_config: Dict[str, Any] = field(default_factory=dict)
    kms_key_arn: Optional[str] = None
    tracing_config: Dict[str, Any] = field(default_factory=dict)
    
    # VPC configuration
    vpc_config: Dict[str, Any] = field(default_factory=dict)
    
    # Layers
    layers: List[Dict[str, Any]] = field(default_factory=list)
    
    # State and package type
    state: Optional[str] = None
    state_reason: Optional[str] = None
    state_reason_code: Optional[str] = None
    last_update_status: Optional[str] = None
    last_update_status_reason: Optional[str] = None
    last_update_status_reason_code: Optional[str] = None
    package_type: Optional[str] = None
    
    # Architecture and image config
    architectures: List[str] = field(default_factory=list)
    ephemeral_storage: Dict[str, Any] = field(default_factory=dict)
    image_config: Dict[str, Any] = field(default_factory=dict)
    
    # Code signing
    code_signing_config_arn: Optional[str] = None
    signing_profile_version_arn: Optional[str] = None
    signing_job_arn: Optional[str] = None
    
    # Additional configurations  
    aliases: List[Dict[str, Any]] = field(default_factory=list)
    versions: List[Dict[str, Any]] = field(default_factory=list)
    event_source_mappings: List[Dict[str, Any]] = field(default_factory=list)
    event_invoke_configs: List[Dict[str, Any]] = field(default_factory=list)
    concurrency_config: Dict[str, Any] = field(default_factory=dict)
    
    # Policies and permissions
    policy: Dict[str, Any] = field(default_factory=dict)
    
    # Tags
    tags: List[Dict[str, str]] = field(default_factory=list)
    
    # Reserved concurrency
    reserved_concurrent_executions: Optional[int] = None
    
    def __post_init__(self):
        if isinstance(self.last_modified, datetime):
            self.last_modified = self.last_modified.isoformat()


@dataclass  
class LambdaLayer:
    # Basic layer information
    layer_name: str
    layer_arn: str
    scan_id: str
    version: Optional[int] = None
    description: Optional[str] = None
    created_date: Optional[str] = None
    
    # Content and code
    content: Dict[str, Any] = field(default_factory=dict)
    compatible_runtimes: List[str] = field(default_factory=list)
    compatible_architectures: List[str] = field(default_factory=list)
    
    # License and policy
    license_info: Optional[str] = None
    policy: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert datetime objects to ISO format strings if needed"""
        if isinstance(self.created_date, datetime):
            self.created_date = self.created_date.isoformat()


@dataclass
class LambdaEnumerationResult:
    # Functions and layers
    functions: List[LambdaFunction] = field(default_factory=list)
    layers: List[LambdaLayer] = field(default_factory=list)
    
    # Summary statistics
    total_functions: int = 0
    total_layers: int = 0
    
    # Runtime breakdown
    runtime_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Memory and timeout statistics
    memory_stats: Dict[str, Any] = field(default_factory=dict)
    timeout_stats: Dict[str, Any] = field(default_factory=dict)
    
    # Code size statistics
    code_size_stats: Dict[str, Any] = field(default_factory=dict)
    
    # VPC usage
    vpc_functions: List[str] = field(default_factory=list)
    
    # Functions with layers
    functions_with_layers: List[str] = field(default_factory=list)
    
    # Dead letter queues
    functions_with_dlq: List[str] = field(default_factory=list)
    
    # Tracing enabled functions
    functions_with_tracing: List[str] = field(default_factory=list)
    
    # Environment variables usage
    functions_with_env_vars: List[str] = field(default_factory=list)
    
    # Regional information
    region: Optional[str] = None
    
    # Enumeration metadata
    enumeration_time: Optional[str] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    
    def __post_init__(self):
        self.total_functions = len(self.functions)
        self.total_layers = len(self.layers)
        
        # Runtime distribution
        runtime_counts = {}
        memory_sizes = []
        timeouts = []
        code_sizes = []
        
        for func in self.functions:
            # Runtime distribution
            if func.runtime:
                runtime_counts[func.runtime] = runtime_counts.get(func.runtime, 0) + 1
            
            # Memory sizes
            if func.memory_size:
                memory_sizes.append(func.memory_size)
            
            # Timeouts  
            if func.timeout:
                timeouts.append(func.timeout)
            
            # Code sizes
            if func.code_size:
                code_sizes.append(func.code_size)
            
            # VPC usage
            if func.vpc_config and func.vpc_config.get('VpcId'):
                self.vpc_functions.append(func.function_name)
            
            # Layers usage
            if func.layers:
                self.functions_with_layers.append(func.function_name)
            
            # Dead letter queues
            if func.dead_letter_config and func.dead_letter_config.get('TargetArn'):
                self.functions_with_dlq.append(func.function_name)
            
            # Tracing
            if func.tracing_config and func.tracing_config.get('Mode') == 'Active':
                self.functions_with_tracing.append(func.function_name)
            
            # Environment variables
            if func.environment and func.environment.get('Variables'):
                self.functions_with_env_vars.append(func.function_name)
        
        self.runtime_distribution = runtime_counts
        
        # Memory statistics
        if memory_sizes:
            self.memory_stats = {
                'min': min(memory_sizes),
                'max': max(memory_sizes),
                'avg': sum(memory_sizes) / len(memory_sizes),
                'total': len(memory_sizes)
            }
        
        # Timeout statistics
        if timeouts:
            self.timeout_stats = {
                'min': min(timeouts),
                'max': max(timeouts), 
                'avg': sum(timeouts) / len(timeouts),
                'total': len(timeouts)
            }
        
        # Code size statistics
        if code_sizes:
            self.code_size_stats = {
                'min': min(code_sizes),
                'max': max(code_sizes),
                'avg': sum(code_sizes) / len(code_sizes),
                'total_size': sum(code_sizes),
                'total_functions': len(code_sizes)
            }
        
        # Set enumeration time if not provided
        if not self.enumeration_time:
            self.enumeration_time = datetime.now().isoformat()


@dataclass
class LambdaEventSourceMapping:
    uuid: str
    function_name: str
    event_source_arn: str
    batch_size: Optional[int] = None
    maximum_batching_window_in_seconds: Optional[int] = None
    parallelization_factor: Optional[int] = None
    starting_position: Optional[str] = None
    starting_position_timestamp: Optional[str] = None
    state: Optional[str] = None
    state_transition_reason: Optional[str] = None
    last_modified: Optional[str] = None
    last_processing_result: Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.last_modified, datetime):
            self.last_modified = self.last_modified.isoformat()
        if isinstance(self.starting_position_timestamp, datetime):
            self.starting_position_timestamp = self.starting_position_timestamp.isoformat()


@dataclass
class LambdaAlias:
    alias_arn: str
    name: str
    function_version: str
    description: Optional[str] = None
    routing_config: Dict[str, Any] = field(default_factory=dict)
    revision_id: Optional[str] = None