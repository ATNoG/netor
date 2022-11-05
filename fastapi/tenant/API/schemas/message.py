# @Author: Daniel Gomes
# @Date:   2022-08-29 15:15:55
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-03 00:38:59

from pydantic import BaseModel
from typing import Dict, List, Union

class DomainPlacement(BaseModel):
    domainId: str
    componentName: str

class CreateVsiData(BaseModel):
    name: str
    description: str
    vsdId: str
    domainPlacements: List[DomainPlacement] = []
    additionalConf: List[Dict] = []

class DeleteVsiData(BaseModel):
    ola: str

class TenantInfoData(BaseModel):
    username: str
    group: str
    roles: List[str]


class Message(BaseModel):
    vsiId: int
    msgType: str = None
    message: str = ""
    error: bool = False
    tenantId: str = None
    data: Union[CreateVsiData, TenantInfoData] = None