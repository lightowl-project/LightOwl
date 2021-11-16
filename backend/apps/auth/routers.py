from .tools import authenticate_user, check_password_length, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, hash_password, verify_password
from .schema import APIKeyCreateSchema, UserCreateSchema, UserUpdateSchema, APIKeySchema, LightOwlInstallSchema, UserSchema
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ..common import BothAuthParams, UserAuthParams
from toolkits.paginate import TableParam, paginate
from starlette.responses import Response
from datetime import datetime, timedelta
from apps.config.models import Config
from apps.agent.models import Agent
from .models import ApiKey
from config import settings
from .models import User
import logging.config
import ipaddress
import logging
import secrets

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")

router: APIRouter = APIRouter()


@router.post("/install", status_code=status.HTTP_201_CREATED)
async def create_user(form: LightOwlInstallSchema):
    nb_users = User.objects.count()
    if nb_users > 0:
        raise HTTPException(status_code=401, detail="LightOwl is already configured")

    if form.password != form.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords mismatch")

    try:
        ipaddress.IPv4Address(form.ip_address)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Server IP")

    hashed_password = hash_password(form.password)
    User.objects.create(
        username=form.username,
        hashed_password=hashed_password
    )

    Config.objects.create(
        ip_address=form.ip_address,
        agent_token=form.lightowl_token
    )


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user": user.username}, expires_delta=access_token_expires
    )

    user.last_seen = datetime.utcnow()
    user.save()
    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.post('/verify')
async def verify_access_token(app = Depends(BothAuthParams)):
    return True


@router.get("/profile", response_model=UserSchema)
async def profile(app = Depends(BothAuthParams)):
    return app.user


@router.put("/profile", status_code=status.HTTP_204_NO_CONTENT)
async def update_profile(user_update: UserUpdateSchema, app = Depends(BothAuthParams)):
    user = app.user
    user.username = user_update.username
    if user_update.current_password:
        if not verify_password(user_update.current_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid password")

        if not check_password_length(user_update.new_password):
            raise HTTPException(status_code=400, detail="Password not strong enough")

        if user_update.new_password != user_update.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords mismatch")
        
        new_hashed_password: str = hash_password(user_update.new_password)
        user.hashed_password = new_hashed_password

    user.save()


@router.get("/apikey")
async def get_apikey(pagination: TableParam = Depends(), app = Depends(UserAuthParams)):
    api_keys: dict = paginate(ApiKey, pagination, APIKeySchema)
    return api_keys


@router.post("/apikey")
async def create_apikey(api_key: APIKeyCreateSchema, app = Depends(UserAuthParams)):
    generated_key = secrets.token_urlsafe(128)

    apikey: ApiKey = ApiKey(
        user=app.user,
        api_key=generated_key,
        expire=api_key.expire,
        expire_at=api_key.expire_at
    )

    try:
        doc = apikey.save()
        return {"api_key": doc.api_key}
    except Exception:
        raise HTTPException(status_code=500)


@router.delete("/apikey/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_apikey(api_key_id: str, app = Depends(UserAuthParams)):
    try:
        api_key: ApiKey = ApiKey.objects(pk=api_key_id).get()
        api_key.delete()

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ApiKey.DoesNotExist:
        raise HTTPException(status_code=404)


@router.get("/users")
async def get_users(pagination: TableParam = Depends(), app = Depends(BothAuthParams)):
    users: dict = paginate(User, pagination, UserSchema)
    return users
    

@router.post("/users")
async def create_user(user_create: UserCreateSchema, app = Depends(BothAuthParams)):
    if user_create.username == "":
        raise HTTPException(status_code=400, detail="Please set a username")

    if user_create.password != user_create.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords mismatch")

    if len(user_create.password) < 8:
        raise HTTPException(status_code=400, detail="Password must contain at least 8 caracters")

    hashed_password = hash_password(user_create.password)
    user: User = User.objects.create(
        username=user_create.username,
        hashed_password=hashed_password
    )

    user.save()

@router.post("/users/{user_id}/update")
async def update_user(user_id: str, user_schema: UserUpdateSchema, app = Depends(BothAuthParams)):
    try:
        user = User.objects(pk=user_id).get()
        if user.username == "admin":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin user can't be disabled")

        user.disabled = user_schema.disabled
        user.save()
    except User.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, app = Depends(BothAuthParams)):
    try:
        user = User.objects(pk=user_id).get()
        if user.username == "admin":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin user can't be deleted")

        user.delete()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    