from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import ALGORITHM
from app.db.session import get_db
from app.models import Client, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_error
    except JWTError as exc:
        raise credentials_error from exc

    user = db.get(User, int(user_id))
    if user is None:
        raise credentials_error
    return user


def get_optional_current_user(db: Session = Depends(get_db), token: str | None = Depends(optional_oauth2_scheme)) -> User | None:
    if not token:
        return None
    return get_current_user(db, token)


def require_roles(*roles: str) -> Callable[[User], User]:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user

    return dependency


def get_client_for_user(db: Session, user: User) -> Client | None:
    query = db.query(Client)
    if user.telegram_id:
        client = query.filter(Client.telegram_chat_id.isnot(None), Client.email == user.email).first()
        if client:
            return client
    return query.filter(Client.email == user.email).first()


def ensure_staff_or_owner(db: Session, user: User, client_id: int) -> None:
    if user.role in {"manager", "admin", "director"}:
        return
    client = get_client_for_user(db, user)
    if not client or client.id != client_id:
        raise HTTPException(status_code=403, detail="Client can access only own data")
