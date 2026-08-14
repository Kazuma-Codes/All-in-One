from sqlalchemy.orm import Session

from .config import settings
from .security import hash_password
from ..models.user import User


def ensure_admin_user(db: Session) -> str | None:
    """Create or promote the admin account from ADMIN_EMAIL/ADMIN_PASSWORD env vars.

    Insecure to run with the default SECRET_KEY in production; guard is in main.py.
    Returns a short message describing what was done, or None if no-op.
    """
    email = settings.ADMIN_EMAIL
    password = settings.ADMIN_PASSWORD

    if not email or not password:
        return None

    email = email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if user:
        user.is_admin = True
        user.password_hash = hash_password(password)
        action = "promoted admin"
    else:
        user = User(
            email=email,
            password_hash=hash_password(password),
            is_admin=True,
        )
        db.add(user)
        action = "created admin"

    db.commit()

    if settings.APP_ENV == "production":
        return f"Admin bootstrap: {action} ({email}). Consider removing ADMIN_PASSWORD after first login."
    return f"Admin bootstrap: {action} ({email})."