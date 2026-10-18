from email_validator import validate_email, EmailNotValidError
from disposable_email_domains import blocklist


def _is_disposable_email(email: str) -> bool:
    domain = email.split('@')[-1].lower()
    return domain in blocklist


def validate_email_address(email: str) -> tuple[bool, str]:
    try:
        # Validate email format and check MX records
        validate_email(email, check_deliverability=True)
        
        # Check if email domain is disposable
        if _is_disposable_email(email):
            return False, "Disposable email addresses are not allowed"
        
        return True, ""
        
    except EmailNotValidError as e:
        return False, "Email is not valid"