from datetime import datetime
from fastapi import Request
import mongoengine


class User(mongoengine.Document):
    username = mongoengine.StringField()
    first_seen = mongoengine.DateTimeField(default=datetime.utcnow)
    last_seen = mongoengine.DateTimeField(default=datetime.utcnow)
    disabled = mongoengine.BooleanField(default=False)
    hashed_password = mongoengine.StringField()


class ApiKey(mongoengine.Document):
    name = mongoengine.StringField()
    api_key = mongoengine.StringField()
    created_at = mongoengine.DateTimeField(default=datetime.utcnow)
    expire = mongoengine.BooleanField(default=False)
    expire_at = mongoengine.DateField()
    user = mongoengine.ReferenceField(User, reverse_delete_rule=mongoengine.CASCADE)



async def get_user(username: str) -> User:
    try:
        return User.objects(username=username).get()
    except User.DoesNotExist:
        return None
