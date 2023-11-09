from pydantic import BaseModel
from typing import Optional


class UserModel(BaseModel):
    key_id: str
    name: str
    password: str
    server_port: str
    method: str
    access_url: str
    data_limit: str


class NewUserResponseModel(BaseModel):
    status: Optional[str]
    data: Optional[UserModel]


class NewUserModel(BaseModel):
    name: str
