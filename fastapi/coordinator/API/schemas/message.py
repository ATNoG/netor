# @Author: Daniel Gomes
# @Date:   2022-09-08 10:54:45
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-12 17:40:17

from pydantic import BaseModel
from typing import Any, Dict, List, Union
from schemas.vertical import DomainPlacement, DomainPlacementBase


class CreateVsiData(BaseModel):
    name: str
    description: str
    vsdId: str
    vsiId: str
    domainPlacements: List[DomainPlacementBase] = []
    additionalConf: List[Dict] = []    

class StatusUpdateData(BaseModel):
    status: str

class PrimitiveData(BaseModel):
    primitiveName: str
    primitiveTarget: str
    primitiveInternalTarget: str
    primitiveParams: Dict = {}

class ActionUpdateData(BaseModel):
    actionId: str
    status: str
    output: str

class Message(BaseModel):
    vsiId: str
    msgType: str = None
    message: str = ""
    error: bool = False
    tenantId: str = None
    data: Union[CreateVsiData, ActionUpdateData, StatusUpdateData,
                PrimitiveData] = None
