from enum import Enum
from pydantic import BaseModel, Field
from typing import Union, Optional


class AuthEvents(Enum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    AUTH_CHECK = "AUTH_CHECK"
    ACCESS_TOKEN_REFRESH = "ACCESS_TOKEN_REFRESH"


class LoginResponse(BaseModel):
    access_token: Optional[str] = Field(
        None, description="The access token for successful authentication"
    )
    refresh_token: Optional[str] = Field(
        None, description="The refresh token for successful authentication"
    )
    token_type: Optional[str] = Field(
        None, description="The type of token provided, typically 'bearer'"
    )
    detail: Optional[str] = Field(
        None, description="Details about errors, if any occur"
    )
    status_code: int = Field(..., description="HTTP status code of the response")
