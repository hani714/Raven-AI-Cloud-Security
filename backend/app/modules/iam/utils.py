from dataclasses import asdict
from typing import Dict, Any

from .models import IAMEnumerationResult


class FormatConverter:
    @staticmethod
    def to_dict(result: IAMEnumerationResult) -> Dict[str, Any]:
        return asdict(result)

    @staticmethod
    def to_pentest_format(result: IAMEnumerationResult) -> Dict[str, Any]:
        
        # Extract high-risk findings
        high_risk_users = []
        for user in result.users:
            risk_factors = []
            
            # Check for admin policies
            for policy in user.managed_policies:
                if 'admin' in policy['policy_name'].lower():
                    risk_factors.append(f"Has admin policy: {policy['policy_name']}")
            
            # Check for multiple access keys
            if len(user.access_keys) > 1:
                risk_factors.append(f"Multiple access keys: {len(user.access_keys)}")
            
            # Check for inactive access keys
            inactive_keys = [key for key in user.access_keys if key['status'] == 'Inactive']
            if inactive_keys:
                risk_factors.append(f"Inactive access keys: {len(inactive_keys)}")
            
            if risk_factors:
                high_risk_users.append({
                    "username": user.username,
                    "risk_factors": risk_factors,
                    "groups": user.groups,
                    "managed_policies": [p['policy_name'] for p in user.managed_policies]
                })
        
        # Extract assumable roles
        assumable_roles = []
        for role in result.roles:
            trust_policy = role.assume_role_policy
            principals = []
            
            if 'Statement' in trust_policy:
                for statement in trust_policy['Statement']:
                    if statement.get('Effect') == 'Allow' and 'Principal' in statement:
                        principals.append(statement['Principal'])
            
            assumable_roles.append({
                "role_name": role.role_name,
                "principals": principals,
                "managed_policies": [p['policy_name'] for p in role.managed_policies],
                "inline_policies": [p['policy_name'] for p in role.inline_policies]
            })
        
        return {
            "summary": {
                "total_users": len(result.users),
                "total_roles": len(result.roles),
                "total_groups": len(result.groups),
                "high_risk_users": len(high_risk_users),
                "enumeration_time": result.enumeration_time,
                "error_count": len(result.errors)
            },
            "current_user": result.current_user,
            "high_risk_users": high_risk_users,
            "assumable_roles": assumable_roles,
            "groups_with_members": [
                {
                    "group_name": group.group_name,
                    "members": group.members,
                    "managed_policies": [p['policy_name'] for p in group.managed_policies]
                }
                for group in result.groups if group.members
            ],
            "errors": result.errors,
            "permissions_checked": result.permissions_checked
        }


class PolicyAnalyzer:
    @staticmethod
    def find_admin_policies(result: IAMEnumerationResult) -> Dict[str, list]:
        admin_entities = {"users": [], "roles": []}
        
        admin_keywords = ['admin', 'full', 'all', '*']
        
        for user in result.users:
            for policy in user.managed_policies:
                if any(keyword in policy['policy_name'].lower() for keyword in admin_keywords):
                    admin_entities["users"].append({
                        "name": user.username,
                        "policy": policy['policy_name']
                    })
        
        for role in result.roles:
            for policy in role.managed_policies:
                if any(keyword in policy['policy_name'].lower() for keyword in admin_keywords):
                    admin_entities["roles"].append({
                        "name": role.role_name,
                        "policy": policy['policy_name']
                    })
        
        return admin_entities

    @staticmethod
    def find_cross_account_roles(result: IAMEnumerationResult) -> list:
        cross_account_roles = []
        
        for role in result.roles:
            trust_policy = role.assume_role_policy
            
            if 'Statement' in trust_policy:
                for statement in trust_policy['Statement']:
                    if (statement.get('Effect') == 'Allow' and 
                        'Principal' in statement and 
                        isinstance(statement['Principal'], dict) and 
                        'AWS' in statement['Principal']):
                        
                        principal = statement['Principal']['AWS']
                        if isinstance(principal, str) and ':root' in principal:
                            cross_account_roles.append({
                                "role_name": role.role_name,
                                "trusted_account": principal,
                                "conditions": statement.get('Condition', {})
                            })
        
        return cross_account_roles