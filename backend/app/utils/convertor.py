from dataclasses import asdict, is_dataclass


def _to_plain_dict(item):
    if isinstance(item, dict):
        return item
    if is_dataclass(item):
        return asdict(item)
    if hasattr(item, "model_dump"):
        return item.model_dump()
    if hasattr(item, "dict"):
        return item.dict()
    return item

def convert_dataclasses_to_dict(enum_data: dict) -> dict:
    return {
        'iam_users': [_to_plain_dict(user) for user in enum_data.get('iam_users', [])],
        'iam_roles': [_to_plain_dict(role) for role in enum_data.get('iam_roles', [])],
        'iam_groups': [_to_plain_dict(group) for group in enum_data.get('iam_groups', [])],
        'iam_controls': [_to_plain_dict(control) for control in enum_data.get('iam_controls', [])],
        's3_buckets': [_to_plain_dict(bucket) for bucket in enum_data.get('s3_buckets', [])],
        'lambda_functions': [_to_plain_dict(func) for func in enum_data.get('lambda_functions', [])],
        'lambda_layers': [_to_plain_dict(layer) for layer in enum_data.get('lambda_layers', [])]
    }