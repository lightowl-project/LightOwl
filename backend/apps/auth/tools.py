from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.api_key import APIKeyHeader
from datetime import datetime, timedelta, date
from fastapi.param_functions import Security
from .models import get_user, User, ApiKey
from passlib.context import CryptContext
from typing import Optional, Union, Any
from apps.config.models import Config
from jose import JWTError, jwt
from config import settings
from redis import Redis

pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token", auto_error=False)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

API_KEY_NAME = "api_key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def check_password_length(password):
    return len(password) >= 8


async def authenticate_user(username: str, password: str) -> Union[User, bool]:
    if (user := await get_user(username)) is None:
        return False

    if not pwd_context.verify(password, user.hashed_password):
        return False

    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode: dict = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    redis_conn: Redis = Redis(host=settings.REDIS_URL, port=settings.REDIS_PORT, decode_responses=True)
    redis_conn.hmset(encoded_jwt, {
        "username": data["user"]
    })
    redis_conn.expire(encoded_jwt, expires_delta)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if token is None:
        return False

    redis_conn: Redis = Redis(host=settings.REDIS_URL, port=settings.REDIS_PORT, decode_responses=True)
    data = redis_conn.hgetall(token)
    if not data:
        return False

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if (username := payload.get("user")) is None:
            return False
    except JWTError:
        return False

    return await get_user(username=username)


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user:
        return False

    if current_user.disabled:
        return False

    return current_user


async def is_agent_token(api_key_header: str = Security(api_key_header)) -> Any:
    if not api_key_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        Config.objects(agent_token=api_key_header).get()
        return True
    except Config.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


async def is_authenticated(current_user: User = Depends(get_current_active_user), api_key_header: str = Security(api_key_header)) -> Any:
    # This method check if an User is connected or if the API KEY is correct
    if not current_user and not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    elif current_user:
        return current_user
    
    elif api_key_header:
        try:
            api_key: ApiKey = ApiKey.objects(api_key=api_key_header).get()
        except ApiKey.DoesNotExist:
            api_key = None

        if not api_key or (api_key.expire and api_key.expire_at < date.today()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API Key Expired",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return api_key