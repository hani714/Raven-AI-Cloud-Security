from typing import Dict, List, Any


class RiskAnalyzer:
    # High-risk AWS managed policies
    HIGH_RISK_POLICIES = {
        'AdministratorAccess': 'critical',
        'PowerUserAccess': 'high',
        'IAMFullAccess': 'high',
        'SecurityAudit': 'medium',
        'ReadOnlyAccess': 'low'
    }
    
    # Dangerous actions
    DANGEROUS_ACTIONS = {
        'iam:CreateAccessKey',
        'iam:CreateUser',
        'iam:AttachUserPolicy',
        'iam:PutUserPolicy',
        'sts:AssumeRole',
        'lambda:UpdateFunctionCode',
        'lambda:CreateFunction',
        's3:PutBucketPolicy',
        's3:DeleteBucketPolicy',
        'ec2:RunInstances'
    }
    
    def __init__(self):
        self.findings = []
    
    def analyze(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        self.findings = []
        
        # Analyze IAM
        iam_score = self._analyze_iam(processed_data.get('iam', {}))
        
        # Analyze S3
        s3_score = self._analyze_s3(processed_data.get('s3', []))
        
        # Analyze Lambda
        lambda_score = self._analyze_lambda(processed_data.get('lambda', {}))
        
        # Calculate overall severity
        max_score = max(iam_score, s3_score, lambda_score)
        severity = self._calculate_severity(max_score)
        
        return {
            'overall_severity': severity,
            'scores': {
                'iam': iam_score,
                's3': s3_score,
                'lambda': lambda_score
            },
            'findings': self.findings,
            'metadata': processed_data.get('metadata', {})
        }
    
    def _analyze_iam(self, iam_data: Dict[str, Any]) -> int:
        score = 0
        
        # Check users
        for user in iam_data.get('users', []):
            # Check for high-risk policies
            for policy in user.get('managed_policies', []):
                policy_name = policy.get('name', '')
                if policy_name in self.HIGH_RISK_POLICIES:
                    risk_level = self.HIGH_RISK_POLICIES[policy_name]
                    score += 100 if risk_level == 'critical' else 50
                    self.findings.append({
                        'type': 'iam_user_high_risk_policy',
                        'severity': risk_level,
                        'resource': f"user:{user.get('username')}",
                        'detail': f"User has {policy_name} policy attached",
                        'impact': 'Potential full account compromise'
                    })
            
            # Check for wildcard permissions
            for policy in user.get('managed_policies', []):
                for stmt in policy.get('statements', []):
                    if stmt.get('actions') == '*' or stmt.get('resources') == '*':
                        score += 80
                        self.findings.append({
                            'type': 'iam_wildcard_permissions',
                            'severity': 'critical',
                            'resource': f"user:{user.get('username')}",
                            'detail': 'Wildcard (*) permissions detected',
                            'impact': 'Unrestricted access to AWS resources'
                        })
            
            # Check for active access keys
            if user.get('access_keys'):
                score += 10
                self.findings.append({
                    'type': 'iam_access_keys',
                    'severity': 'medium',
                    'resource': f"user:{user.get('username')}",
                    'detail': f"{len(user.get('access_keys'))} active access key(s)",
                    'impact': 'Potential credential exposure'
                })
        
        # Check roles
        for role in iam_data.get('roles', []):
            assume_policy = role.get('assume_role_policy', {})
            for stmt in assume_policy.get('Statement', []):
                principal = stmt.get('Principal', {})
                # Check for overly permissive assume role policies
                if principal.get('AWS') == '*':
                    score += 70
                    self.findings.append({
                        'type': 'iam_permissive_assume_role',
                        'severity': 'high',
                        'resource': f"role:{role.get('role_name')}",
                        'detail': 'Role can be assumed by any AWS account',
                        'impact': 'Unauthorized role assumption'
                    })
        
        return min(score, 100)  # Cap at 100
    
    def _analyze_s3(self, s3_data: List[Dict[str, Any]]) -> int:
        score = 0
        
        for bucket in s3_data:
            # Check for public buckets
            if bucket.get('is_public'):
                score += 90
                self.findings.append({
                    'type': 's3_public_bucket',
                    'severity': 'critical',
                    'resource': f"s3:{bucket.get('name')}",
                    'detail': 'Bucket is publicly accessible',
                    'impact': 'Data exposure risk'
                })
            
            # Check public access block
            pab = bucket.get('public_access_block', {})
            if not all([
                pab.get('BlockPublicAcls'),
                pab.get('IgnorePublicAcls'),
                pab.get('BlockPublicPolicy'),
                pab.get('RestrictPublicBuckets')
            ]):
                score += 40
                self.findings.append({
                    'type': 's3_weak_public_access_block',
                    'severity': 'high',
                    'resource': f"s3:{bucket.get('name')}",
                    'detail': 'Public access block not fully enabled',
                    'impact': 'Potential for accidental public exposure'
                })
            
            # Check encryption
            if not bucket.get('encryption'):
                score += 30
                self.findings.append({
                    'type': 's3_no_encryption',
                    'severity': 'medium',
                    'resource': f"s3:{bucket.get('name')}",
                    'detail': 'Bucket encryption not enabled',
                    'impact': 'Data at rest not encrypted'
                })
            
            # Check versioning
            if not bucket.get('versioning_enabled') and bucket.get('has_objects'):
                score += 20
                self.findings.append({
                    'type': 's3_no_versioning',
                    'severity': 'low',
                    'resource': f"s3:{bucket.get('name')}",
                    'detail': 'Versioning not enabled',
                    'impact': 'No protection against accidental deletion'
                })
        
        return min(score, 100)
    
    def _analyze_lambda(self, lambda_data: Dict[str, Any]) -> int:
        score = 0
        
        for func in lambda_data.get('functions', []):
            # Check for environment variables (potential secrets)
            if func.get('has_environment_vars'):
                score += 30
                self.findings.append({
                    'type': 'lambda_environment_variables',
                    'severity': 'medium',
                    'resource': f"lambda:{func.get('name')}",
                    'detail': f"Function has environment variables: {', '.join(func.get('environment_var_keys', [])[:3])}...",
                    'impact': 'Potential credential exposure'
                })
            
            # Check VPC configuration
            if not func.get('in_vpc'):
                score += 10
                self.findings.append({
                    'type': 'lambda_not_in_vpc',
                    'severity': 'low',
                    'resource': f"lambda:{func.get('name')}",
                    'detail': 'Function not in VPC',
                    'impact': 'Reduced network isolation'
                })
        
        return min(score, 100)
    
    def _calculate_severity(self, score: int) -> str:
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 30:
            return 'medium'
        else:
            return 'low'
