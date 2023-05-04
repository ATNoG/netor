from pydantic import BaseModel
from typing import Dict, Union

class AdditionalConf(BaseModel):
    member_vnf_index: str
    primitive: str
    vdu_id: str
    primitive_params: Dict = {}


class ActionNsData(BaseModel):
    primitiveName: str = None
    domainId: str
    nsId: str = None
    actionId: str = None # Id given by the Coordinator to identify the Action
    isAlarm: bool = False # Flag to identify the Alarm Day-2 Actions
    additionalConf: Dict


class ActionResponseData(BaseModel):
    primitiveName: str = None
    actionId: str # Id given by the Coordinator to identify the Action(Primitive)
    nfvoId: str # Id given by the NFVO to identify the Action(Primitive)
    isAlarm: bool = False # Flag to identify the Alarm Day-2 Actions
    status: str
    output: str



class FetchPrimitiveData(BaseModel):
    domainId: str
    nfvoId: str = None
    isAlarm: bool = False # Flag to identify the Alarm Day-2 Actions
    actionId: str

class FetchNsInfoData(BaseModel):
    domainId: str
    nsId: str

class Message(BaseModel):
    vsiId: int
    msgType: str = None
    message: str = ""
    error: bool = False
    tenantId: str = None
    data: Union[ActionNsData, ActionResponseData,
                FetchNsInfoData,  FetchPrimitiveData] = None