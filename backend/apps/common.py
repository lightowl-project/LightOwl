from .auth.tools import is_authenticated, is_agent_token
from .auth.models import ApiKey, User
from fastapi import Request, Depends
from typing import Union


class BothAuthParams:
    """Common parameters for API who accepts API Key or User for Authentication"""    
    def __init__(self, request: Request, current_user: Union[ApiKey, User] = Depends(is_authenticated)) -> None:
        self.request = request
        self.user = current_user


class UserAuthParams:
    def __init__(self, request: Request, current_user: User = Depends(is_authenticated)) -> None:
        self.request = request
        self.user = current_user



class AgentAuthParams:
    def __init__(self, request: Request, agent_token = Depends(is_agent_token)) -> None:
        self.request = request
        self.agent_token = agent_token
