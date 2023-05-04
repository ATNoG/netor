# @Author: Daniel Gomes
# @Date:   2022-08-16 16:40:08
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-05 14:02:58

from pydantic import BaseModel
from typing import Any, Dict, List, Union


class DomainInfoData(BaseModel):
    domainIds: List


class CreateVsiData(BaseModel):
    name: str
    description: str
    vsdId: str
    domainPlacements: Any
    additionalConf: Any


class InstantiateNsiData(BaseModel):
    name: str
    description: str = None
    domainId: str = None
    nstId: str = None
    additionalConf: str = None


class InstantiateNsData(BaseModel):
    name: str
    description: str = None
    domainId: str = None
    nsdId: str = None
    additionalConf: str = None




class UpdateResourcesNfvoIdsData(BaseModel):
    componentName: str
    componentId: str
    additionalData: Dict[str, str]


class ActionNsData(BaseModel):
    primitiveName: str = None
    domainId: str = None
    actionId: str # Id given by the Coordinator to identify the Action
    isAlarm: bool = False # Flag to identify the Alarm Day-2 Actions
    nsId: str = None
    additionalConf: Dict


class ActionResponseData(BaseModel):
    primitiveName: str = None
    actionId: str # Id given by the Coordinator to identify the Action
    nfvoId: str # Id given by the NFVO to identify the Action
    isAlarm: bool = False # Flag to identify the Alarm Day-2 Actions
    status: str 
    output: str


class FecthNsiInfoData(BaseModel):
    domainId: str
    nsiId: str

class FetchNsInfoData(BaseModel):
    domainId: str
    nsId: str

class FetchPrimitiveData(BaseModel):
    domainId: str
    nfvoId: str
    actionId: Union[int, str]
    isAlarm: bool = False # Flag to identify the Alarm Day-2 Actions

class NsiInfoData(BaseModel):
    nsiId: str
    nsiInfo: Any = None

class NsInfoData(BaseModel):
    nsId: str
    nsInfo: Any = None

class DeleteNsiData(BaseModel):
    domainId: str
    nsiId: str
    force: bool

class DeleteNsData(BaseModel):
    domainId: str
    nsId: str
    force: bool

class Message(BaseModel):
    vsiId: Union[int,str]
    msgType: str = None
    message: str = ""
    error: bool = False
    tenantId: str = None
    data: Union[DomainInfoData, CreateVsiData,InstantiateNsData,
                InstantiateNsData, UpdateResourcesNfvoIdsData,
                ActionNsData, ActionResponseData, FetchPrimitiveData,
                DeleteNsiData, FetchNsInfoData, FecthNsiInfoData,
                 NsiInfoData, NsInfoData, DeleteNsData] = None
