from ..core.config import settings


def is_guest_user(user) -> bool:
    return bool(user.email and user.email.endswith(f"@{settings.GUEST_EMAIL_DOMAIN}"))
