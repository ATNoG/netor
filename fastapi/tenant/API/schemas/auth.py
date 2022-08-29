# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-24 17:59:10

# generic imports
from typing import List
from pydantic import BaseModel


class Vsd(BaseModel):
    id: str


class Vsi(BaseModel):
    id: str


class SlaConstraintBase(BaseModel):
    storage: int
    memory: int
    vcpu: int
    scope: int
    location: str


class SlaConstraintCreate(SlaConstraintBase):
    pass


class SlaContraint(SlaConstraintBase):
    id: int


class SlaBase(BaseModel):
    enabled: bool


class SlaCreate(SlaBase):
    constraints: SlaConstraintCreate


class Sla(SlaBase):
    id: int
    constraints: SlaContraint


class TenantBase(BaseModel):
    username: str
    group: str
    vsds: List[Vsd] = []
    vsis: List[Vsi] = []
    slas: List[Sla] = []


class TenantCreate(TenantBase):
    password: str
    roles: List[str]
    slas: List[SlaCreate] = []


class Tenant(TenantBase):
    id: int
    roles: List[str]
    slas: List[Sla] = []


class TenantLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class NewPassword(BaseModel):
    new_password: str


class TenantInfo(BaseModel):
    username: str
    roles: List[str]
