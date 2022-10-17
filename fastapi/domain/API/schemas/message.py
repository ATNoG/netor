# @Author: Daniel Gomes
# @Date:   2022-08-16 16:40:08
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-12 10:20:58

from pydantic import BaseModel
from typing import Any, Dict, List, Union


class DomainInfoData(BaseModel):
    domainIds: List


class InstantiateNsiData(BaseModel):
    name: str
    description: str = None
    domainId: str = None
    nstId: str = None
    additionalConf: str = None


class UpdateResourcesNfvoIdsData(BaseModel):
    componentName: str
    componentId: str
    additionalData: Dict[str, str]


class ActionNsData(BaseModel):
    primitiveName: str = None
    domainId: str = None
    nsId: str = None
    additionalConf: Dict


class ActionResponseData(BaseModel):
    primitiveName: str = None
    actionId: str # Id given by the Coordinator to identify the Action
    nfvoId: str # Id given by the NFVO to identify the Action
    status: str 
    output: str


class FecthNsiInfoData(BaseModel):
    domainId: str = None
    nsiId: str = None

class FetchPrimitiveData(BaseModel):
    domainId: str
    nfvoId: str
    actionId: str

class NsiInfoData(BaseModel):
    nsiId: str
    nsiInfo: Any = None


class Message(BaseModel):
    vsiId: int
    msgType: str = None
    message: str = ""
    error: bool = False
    tenantId: str = None
    data: Union[DomainInfoData,
                InstantiateNsiData, UpdateResourcesNfvoIdsData,
                ActionNsData, ActionResponseData, FetchPrimitiveData,
                FecthNsiInfoData, NsiInfoData] = None
