from typing import Dict, List, Any
import copy


class DataPreprocessor:
    # Keys to always remove (AWS metadata noise)
    NOISE_KEYS = {
        'ResponseMetadata', 'HTTPStatusCode', 'HTTPHeaders', 'RetryAttempts',
        'RequestId', 'HostId', 'x-amz-id-2', 'x-amz-request-id', 'date',
        'content-type', 'transfer-encoding', 'server'
    }
    
    @staticmethod
    def clean_dict(data: Dict[str, Any], max_depth: int = 10) -> Dict[str, Any]:
        if max_depth == 0:
            return data
            
        cleaned = {}
        for key, value in data.items():
            if key in DataPreprocessor.NOISE_KEYS:
                continue
                
            if isinstance(value, dict):
                cleaned_value = DataPreprocessor.clean_dict(value, max_depth - 1)
                if cleaned_value:  # Only add non-empty dicts
                    cleaned[key] = cleaned_value
            elif isinstance(value, list):
                cleaned_list = [
                    DataPreprocessor.clean_dict(item, max_depth - 1) if isinstance(item, dict) else item
                    for item in value
                ]
                if cleaned_list:  # Only add non-empty lists
                    cleaned[key] = cleaned_list
            else:
                cleaned[key] = value
                
        return cleaned
    
    @staticmethod
    def extract_iam_security_context(iam_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'users': [
                {
                    'username': user.get('username'),
                    'user_id': user.get('user_id'),
                    'arn': user.get('arn'),
                    'managed_policies': [
                        {
                            'name': p.get('policy_name'),
                            'arn': p.get('policy_arn'),
                            'statements': [
                                {
                                    'effect': stmt.get('Effect'),
                                    'actions': stmt.get('Action'),
                                    'resources': stmt.get('Resource')
                                }
                                for version in p.get('versions', [])
                                if version.get('is_default')
                                for stmt in version.get('document', {}).get('Statement', [])
                            ]
                        }
                        for p in user.get('managed_policies', [])
                    ],
                    'inline_policies': user.get('inline_policies', []),
                    'groups': user.get('groups', []),
                    'access_keys': [
                        {
                            'key_id': key.get('access_key_id'),
                            'status': key.get('status')
                        }
                        for key in user.get('access_keys', [])
                        if key.get('status') == 'Active'
                    ]
                }
                for user in iam_data.get('iam_users', [])
            ],
            'roles': [
                {
                    'role_name': role.get('role_name'),
                    'arn': role.get('arn'),
                    'assume_role_policy': role.get('assume_role_policy'),
                    'managed_policies': [
                        {
                            'name': p.get('policy_name'),
                            'statements': [
                                {
                                    'effect': stmt.get('Effect'),
                                    'actions': stmt.get('Action'),
                                    'resources': stmt.get('Resource')
                                }
                                for version in p.get('versions', [])
                                if version.get('is_default')
                                for stmt in version.get('document', {}).get('Statement', [])
                            ]
                        }
                        for p in role.get('managed_policies', [])
                    ],
                    'inline_policies': role.get('inline_policies', [])
                }
                for role in iam_data.get('iam_roles', [])
            ],
            'groups': [
                {
                    'group_name': group.get('group_name'),
                    'arn': group.get('arn'),
                    'members': group.get('members', []),
                    'managed_policies': [
                        {
                            'name': p.get('policy_name'),
                            'statements': [
                                {
                                    'effect': stmt.get('Effect'),
                                    'actions': stmt.get('Action'),
                                    'resources': stmt.get('Resource')
                                }
                                for version in p.get('versions', [])
                                if version.get('is_default')
                                for stmt in version.get('document', {}).get('Statement', [])
                            ]
                        }
                        for p in group.get('managed_policies', [])
                    ]
                }
                for group in iam_data.get('iam_groups', [])
            ]
        }
    
    @staticmethod
    def extract_s3_security_context(s3_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                'name': bucket.get('name'),
                'region': bucket.get('region'),
                'public_access_block': bucket.get('public_access_block', {}),
                'policy': bucket.get('policy', {}).get('Statement', []),
                'is_public': bucket.get('policy_status', {}).get('IsPublic', False),
                'encryption': bucket.get('encryption_config', {})
                    .get('ServerSideEncryptionConfiguration', {})
                    .get('Rules', [{}])[0]
                    .get('ApplyServerSideEncryptionByDefault', {})
                    .get('SSEAlgorithm') if bucket.get('encryption_config') else None,
                'versioning_enabled': 'Status' in bucket.get('versioning_config', {}),
                'has_objects': bucket.get('object_count', 0) > 0,
                'acl': bucket.get('acl', {}).get('Grants', [])
            }
            for bucket in s3_data
        ]
    
    @staticmethod
    def extract_lambda_security_context(lambda_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'functions': [
                {
                    'name': func.get('function_name'),
                    'arn': func.get('function_arn'),
                    'role': func.get('role'),
                    'runtime': func.get('runtime'),
                    'has_environment_vars': bool(func.get('environment', {}).get('Variables')),
                    'environment_var_keys': list(func.get('environment', {}).get('Variables', {}).keys()),
                    'in_vpc': bool(func.get('vpc_config', {}).get('VpcId')),
                    'has_layers': bool(func.get('layers', [])),
                    'has_policy': bool(func.get('policy', {}))
                }
                for func in lambda_data.get('lambda_functions', [])
            ],
            'layers': [
                {
                    'name': layer.get('layer_name'),
                    'arn': layer.get('layer_arn'),
                    'version': layer.get('version')
                }
                for layer in lambda_data.get('lambda_layers', [])
            ]
        }
    
    @staticmethod
    def preprocess_enumeration_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        # Clean the data
        cleaned = DataPreprocessor.clean_dict(copy.deepcopy(raw_data))
        
        # Extract security contexts
        return {
            'iam': DataPreprocessor.extract_iam_security_context(cleaned),
            's3': DataPreprocessor.extract_s3_security_context(cleaned.get('s3_buckets', [])),
            'lambda': DataPreprocessor.extract_lambda_security_context(cleaned),
            'metadata': {
                'scan_id': raw_data.get('iam_users', [{}])[0].get('scan_id') if raw_data.get('iam_users') else None,
                'total_users': len(raw_data.get('iam_users', [])),
                'total_roles': len(raw_data.get('iam_roles', [])),
                'total_groups': len(raw_data.get('iam_groups', [])),
                'total_s3_buckets': len(raw_data.get('s3_buckets', [])),
                'total_lambda_functions': len(raw_data.get('lambda_functions', [])),
            }
        }
