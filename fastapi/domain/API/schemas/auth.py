# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-23 11:31:18

# generic imports
from typing import List
from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    password: str
    roles: List[str]


class Tenant(BaseModel):
    username: str
    role: str

    def isAdmin(self):
        return self.role == 'ADMIN'


class Token(BaseModel):
    access_token: str
    token_type: str


class NewPassword(BaseModel):
    new_password: str


class UserInfo(BaseModel):
    username: str
    is_active: str
    roles: str
