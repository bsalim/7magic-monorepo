from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=255)


class ChangePasswordRequest(BaseModel):
    # The length rule lives in the service, not in Field, so a rejection comes
    # back in the {"error": {...}} envelope. The app registers no
    # RequestValidationError handler, so a pydantic 422 would reach the CMS
    # with no message it can show.
    current_password: str = Field(min_length=1, max_length=255)
    new_password: str = Field(min_length=1, max_length=255)


class AuthUserResponse(BaseModel):
    id: int
    email: str
    username: str | None
    first_name: str
    last_name: str
    roles: list[str]


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthUserResponse
