import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.rate_limit import limiter
from ...core.security import hash_password, verify_password, create_access_token
from ...core.config import settings
from ...models.user import User
from ...schemas.auth import RegisterRequest, LoginRequest, TokenResponse

router = APIRouter()


@router.post("/guest", response_model=TokenResponse)
@limiter.limit("10/minute")
def guest_login(request: Request, db: Session = Depends(get_db)):
    guest_email = f"guest_{uuid.uuid4().hex}@{settings.GUEST_EMAIL_DOMAIN}"

    user = User(
        email=guest_email,
        password_hash=hash_password(uuid.uuid4().hex)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)