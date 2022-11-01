# @Author: Daniel Gomes
# @Date:   2022-08-16 17:56:17
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-01 15:35:50

from typing import List
from pydantic import BaseModel, AnyHttpUrl, validator
import aux.constants as Constants


class OwnedLayersBase(BaseModel):
    domainLayerId: str
    domainLayerType: str
    username: str
    project: str
    vimAccount: str

    @validator('domainLayerType')
    def layer_type_must_be_valid(cls, v):
        if v not in Constants.DOMAIN_LAYER_TYPES:
            raise ValueError('Domain Layer Type not supported')
        return v


class OwnedLayersCreate(OwnedLayersBase):
    password: str


class OwnedLayers(OwnedLayersBase):
    class Config:
        orm_mode = True


class DomainAgreement(BaseModel):
    domainAgreeWithId: str
    domainLayersListAgreeWith: List[str]


class DomainBase(BaseModel):
    domainId: str
    name: str = None
    description: str = None
    owner: str = None
    admin: str = None
    status: str = None
    url: AnyHttpUrl
    auth: bool = False
    interfaceType: str
    domainAgreement: List[DomainAgreement] = []


class DomainCreate(DomainBase):
    ownedLayers: List[OwnedLayersCreate]


class DomainUpdate(BaseModel):
    name: str = None
    description: str = None
    owner: str = None
    admin: str = None
    status: str = None
    url: AnyHttpUrl
    auth: bool = False
    interfaceType: str
    domainAgreement: List[DomainAgreement] = []
    ownedLayers: List[OwnedLayersCreate]


class Domain(DomainBase):
    ownedLayers: List[OwnedLayers]

    class Config:
        orm_mode = True
