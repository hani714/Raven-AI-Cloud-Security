import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .models import LambdaEnumerationResult, LambdaFunction, LambdaLayer

logger = logging.getLogger(__name__)


class LambdaFormatConverter:
    @staticmethod
    def to_dict(result: LambdaEnumerationResult) -> Dict[str, Any]:
        try:
            # Convert functions to dictionaries
            functions_dict = []
            for func in result.functions:
                func_dict = LambdaFormatConverter._function_to_dict(func)
                functions_dict.append(func_dict)
            
            # Convert layers to dictionaries
            layers_dict = []
            for layer in result.layers:
                layer_dict = LambdaFormatConverter._layer_to_dict(layer)
                layers_dict.append(layer_dict)
            
            return {
                "summary": {
                    "total_functions": result.total_functions,
                    "total_layers": result.total_layers,
                    "region": result.region,
                    "enumeration_time": result.enumeration_time,
                    "runtime_distribution": result.runtime_distribution,
                    "memory_stats": result.memory_stats,
                    "timeout_stats": result.timeout_stats,
                    "code_size_stats": result.code_size_stats,
                    "vpc_functions": result.vpc_functions,
                    "functions_with_layers": result.functions_with_layers,
                    "functions_with_dlq": result.functions_with_dlq,
                    "functions_with_tracing": result.functions_with_tracing,
                    "functions_with_env_vars": result.functions_with_env_vars
                },
                "functions": functions_dict,
                "layers": layers_dict,
                "errors": result.errors
            }
            
        except Exception as e:
            logger.error(f"Error converting Lambda result to dictionary: {str(e)}")
            return {
                "error": f"Conversion failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    def _function_to_dict(function: LambdaFunction) -> Dict[str, Any]:
        return {
            "function_name": function.function_name,
            "function_arn": function.function_arn,
            "runtime": function.runtime,
            "role": function.role,
            "handler": function.handler,
            "code_size": function.code_size,
            "description": function.description,
            "timeout": function.timeout,
            "memory_size": function.memory_size,
            "last_modified": function.last_modified,
            "code_sha256": function.code_sha256,
            "version": function.version,
            "environment": function.environment,
            "dead_letter_config": function.dead_letter_config,
            "kms_key_arn": function.kms_key_arn,
            "tracing_config": function.tracing_config,
            "vpc_config": function.vpc_config,
            "layers": function.layers,
            "state": function.state,
            "state_reason": function.state_reason,
            "state_reason_code": function.state_reason_code,
            "last_update_status": function.last_update_status,
            "last_update_status_reason": function.last_update_status_reason,
            "last_update_status_reason_code": function.last_update_status_reason_code,
            "package_type": function.package_type,
            "architectures": function.architectures,
            "ephemeral_storage": function.ephemeral_storage,
            "image_config": function.image_config,
            "code_signing_config_arn": function.code_signing_config_arn,
            "signing_profile_version_arn": function.signing_profile_version_arn,
            "signing_job_arn": function.signing_job_arn,
            "aliases": function.aliases,
            "versions": function.versions,
            "event_source_mappings": function.event_source_mappings,
            "event_invoke_configs": function.event_invoke_configs,
            "concurrency_config": function.concurrency_config,
            "policy": function.policy,
            "tags": function.tags,
            "reserved_concurrent_executions": function.reserved_concurrent_executions
        }
    
    @staticmethod
    def _layer_to_dict(layer: LambdaLayer) -> Dict[str, Any]:
        return {
            "layer_name": layer.layer_name,
            "layer_arn": layer.layer_arn,
            "version": layer.version,
            "description": layer.description,
            "created_date": layer.created_date,
            "content": layer.content,
            "compatible_runtimes": layer.compatible_runtimes,
            "compatible_architectures": layer.compatible_architectures,
            "license_info": layer.license_info,
            "policy": layer.policy
        }
    
    @staticmethod
    def to_json(result: LambdaEnumerationResult, indent: int = 2) -> str:
        try:
            result_dict = LambdaFormatConverter.to_dict(result)
            return json.dumps(result_dict, indent=indent, default=str)
        except Exception as e:
            logger.error(f"Error converting Lambda result to JSON: {str(e)}")
            return json.dumps({
                "error": f"JSON conversion failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
    
    @staticmethod
    def to_summary_report(result: LambdaEnumerationResult) -> str:
        try:
            report = []
            report.append("=" * 60)
            report.append("AWS LAMBDA ENUMERATION REPORT")
            report.append("=" * 60)
            report.append(f"Region: {result.region}")
            report.append(f"Enumeration Time: {result.enumeration_time}")
            report.append(f"Total Functions: {result.total_functions}")
            report.append(f"Total Layers: {result.total_layers}")
            report.append("")
            
            # Runtime distribution
            if result.runtime_distribution:
                report.append("RUNTIME DISTRIBUTION:")
                report.append("-" * 20)
                for runtime, count in result.runtime_distribution.items():
                    report.append(f"  {runtime}: {count}")
                report.append("")
            
            # Memory statistics
            if result.memory_stats:
                report.append("MEMORY STATISTICS (MB):")
                report.append("-" * 25)
                report.append(f"  Min: {result.memory_stats.get('min', 'N/A')}")
                report.append(f"  Max: {result.memory_stats.get('max', 'N/A')}")
                report.append(f"  Avg: {result.memory_stats.get('avg', 'N/A'):.2f}")
                report.append("")
            
            # Timeout statistics
            if result.timeout_stats:
                report.append("TIMEOUT STATISTICS (seconds):")
                report.append("-" * 30)
                report.append(f"  Min: {result.timeout_stats.get('min', 'N/A')}")
                report.append(f"  Max: {result.timeout_stats.get('max', 'N/A')}")
                report.append(f"  Avg: {result.timeout_stats.get('avg', 'N/A'):.2f}")
                report.append("")
            
            # Code size statistics
            if result.code_size_stats:
                report.append("CODE SIZE STATISTICS:")
                report.append("-" * 25)
                total_size_mb = result.code_size_stats.get('total_size', 0) / (1024 * 1024)
                report.append(f"  Total Size: {total_size_mb:.2f} MB")
                report.append(f"  Min Size: {result.code_size_stats.get('min', 'N/A')} bytes")
                report.append(f"  Max Size: {result.code_size_stats.get('max', 'N/A')} bytes")
                report.append(f"  Avg Size: {result.code_size_stats.get('avg', 'N/A'):.2f} bytes")
                report.append("")
            
            # Special configurations
            report.append("SPECIAL CONFIGURATIONS:")
            report.append("-" * 25)
            report.append(f"  Functions with VPC: {len(result.vpc_functions)}")
            report.append(f"  Functions with Layers: {len(result.functions_with_layers)}")
            report.append(f"  Functions with DLQ: {len(result.functions_with_dlq)}")
            report.append(f"  Functions with Tracing: {len(result.functions_with_tracing)}")
            report.append(f"  Functions with Env Vars: {len(result.functions_with_env_vars)}")
            report.append("")
            
            # Functions list
            if result.functions:
                report.append("LAMBDA FUNCTIONS:")
                report.append("-" * 17)
                for func in result.functions:
                    report.append(f"  {func.function_name}")
                    report.append(f"    Runtime: {func.runtime}")
                    report.append(f"    Memory: {func.memory_size} MB")
                    report.append(f"    Timeout: {func.timeout}s")
                    if func.description:
                        report.append(f"    Description: {func.description}")
                    report.append("")
            
            # Layers list
            if result.layers:
                report.append("LAMBDA LAYERS:")
                report.append("-" * 15)
                for layer in result.layers:
                    report.append(f"  {layer.layer_name} (v{layer.version})")
                    if layer.description:
                        report.append(f"    Description: {layer.description}")
                    report.append(f"    Runtimes: {', '.join(layer.compatible_runtimes)}")
                    report.append("")
            
            # Errors
            if result.errors:
                report.append("ERRORS ENCOUNTERED:")
                report.append("-" * 19)
                for error in result.errors:
                    report.append(f"  {error.get('operation', 'Unknown')}: {error.get('error', 'Unknown error')}")
                report.append("")
            
            report.append("=" * 60)
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"Error generating summary report: {str(e)}")
            return f"Error generating report: {str(e)}"


class LambdaAnalyzer:
    @staticmethod
    def analyze_security_issues(result: LambdaEnumerationResult) -> Dict[str, Any]:
        issues = {
            "high_risk": [],
            "medium_risk": [],
            "low_risk": [],
            "recommendations": []
        }
        
        try:
            for func in result.functions:
                function_issues = LambdaAnalyzer._analyze_function_security(func)
                
                # Merge issues
                for risk_level in ['high_risk', 'medium_risk', 'low_risk']:
                    issues[risk_level].extend(function_issues.get(risk_level, []))
            
            # Generate recommendations
            issues['recommendations'] = LambdaAnalyzer._generate_security_recommendations(issues)
            
            return issues
            
        except Exception as e:
            logger.error(f"Error analyzing security issues: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def _analyze_function_security(func: LambdaFunction) -> Dict[str, List[str]]:
        issues = {"high_risk": [], "medium_risk": [], "low_risk": []}
        
        # Check for overprivileged execution role
        if func.role and "*" in func.role:
            issues["high_risk"].append(f"{func.function_name}: Overly broad IAM role")
        
        # Check for environment variables (potential secrets)
        if func.environment and func.environment.get('Variables'):
            env_vars = func.environment['Variables']
            sensitive_keys = ['password', 'secret', 'key', 'token', 'api_key']
            
            for var_name in env_vars.keys():
                if any(sensitive in var_name.lower() for sensitive in sensitive_keys):
                    issues["medium_risk"].append(
                        f"{func.function_name}: Potential secret in environment variable '{var_name}'"
                    )
        
        # Check for no KMS encryption
        if not func.kms_key_arn and func.environment and func.environment.get('Variables'):
            issues["medium_risk"].append(f"{func.function_name}: Environment variables not encrypted with KMS")
        
        # Check for no dead letter queue
        if not func.dead_letter_config or not func.dead_letter_config.get('TargetArn'):
            issues["low_risk"].append(f"{func.function_name}: No dead letter queue configured")
        
        # Check for no tracing
        tracing_mode = func.tracing_config.get('Mode') if func.tracing_config else None
        if tracing_mode != 'Active':
            issues["low_risk"].append(f"{func.function_name}: X-Ray tracing not enabled")
        
        # Check for high timeout values
        if func.timeout and func.timeout > 300:  # 5 minutes
            issues["medium_risk"].append(f"{func.function_name}: High timeout value ({func.timeout}s)")
        
        # Check for high memory allocation
        if func.memory_size and func.memory_size > 2048:  # 2GB
            issues["low_risk"].append(f"{func.function_name}: High memory allocation ({func.memory_size}MB)")
        
        # Check for VPC configuration (potential networking risks)
        if func.vpc_config and func.vpc_config.get('VpcId'):
            # This is informational - VPC can be good or bad depending on setup
            issues["low_risk"].append(f"{func.function_name}: Function deployed in VPC")
        
        return issues
    
    @staticmethod
    def _generate_security_recommendations(issues: Dict[str, Any]) -> List[str]:
        recommendations = []
        
        if issues.get('high_risk'):
            recommendations.append("Address high-risk issues immediately:")
            recommendations.extend([f"  - {issue}" for issue in issues['high_risk'][:5]])
        
        if issues.get('medium_risk'):
            recommendations.append("Consider addressing medium-risk issues:")
            recommendations.append("  - Use AWS Secrets Manager or Parameter Store for sensitive data")
            recommendations.append("  - Enable KMS encryption for environment variables")
            recommendations.append("  - Review and reduce function timeouts where possible")
        
        if issues.get('low_risk'):
            recommendations.append("Optimization opportunities:")
            recommendations.append("  - Configure dead letter queues for error handling")
            recommendations.append("  - Enable X-Ray tracing for better observability")
            recommendations.append("  - Review memory allocations for cost optimization")
        
        return recommendations
    
    @staticmethod
    def analyze_cost_optimization(result: LambdaEnumerationResult) -> Dict[str, Any]:
        analysis = {
            "potential_savings": [],
            "optimization_opportunities": [],
            "cost_breakdown": {}
        }
        
        try:
            total_memory_gb_seconds = 0
            over_provisioned_functions = []
            
            for func in result.functions:
                # Check for over-provisioned memory
                if func.memory_size and func.memory_size > 1024:  # > 1GB
                    over_provisioned_functions.append({
                        "function": func.function_name,
                        "memory": func.memory_size,
                        "recommendation": "Consider profiling and reducing memory allocation"
                    })
                
                # Estimate monthly cost (very rough calculation)
                if func.memory_size and func.timeout:
                    # Assume 1000 invocations per month for estimation
                    memory_gb = func.memory_size / 1024
                    duration_seconds = func.timeout
                    monthly_gb_seconds = memory_gb * duration_seconds * 1000  # 1000 invocations
                    total_memory_gb_seconds += monthly_gb_seconds
            
            # AWS Lambda pricing: ~$0.0000166667 per GB-second
            estimated_monthly_cost = total_memory_gb_seconds * 0.0000166667
            
            analysis["cost_breakdown"] = {
                "estimated_monthly_cost_usd": round(estimated_monthly_cost, 2),
                "total_gb_seconds_per_month": round(total_memory_gb_seconds, 2),
                "functions_analyzed": len(result.functions)
            }
            
            analysis["optimization_opportunities"] = [
                f"Review {len(over_provisioned_functions)} functions with high memory allocation",
                "Consider using ARM-based architectures for cost savings",
                "Implement function warming strategies to reduce cold starts",
                "Review function timeout settings to prevent unnecessary charges"
            ]
            
            if over_provisioned_functions:
                analysis["potential_savings"] = over_provisioned_functions[:10]  # Top 10
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing cost optimization: {str(e)}")
            return {"error": str(e)}