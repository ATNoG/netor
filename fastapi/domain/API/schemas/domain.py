# @Author: Daniel Gomes
# @Date:   2022-08-16 17:56:17
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-23 11:31:49

from typing import List
from pydantic import BaseModel, AnyHttpUrl


class OwnedLayersBase(BaseModel):
    domainLayerId: str
    domainLayerType: str
    username: str
    project: str
    vimAccount: str


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


class DomainUpdate(DomainCreate):
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
