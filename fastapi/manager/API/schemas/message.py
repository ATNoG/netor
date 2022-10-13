# @Author: Daniel Gomes
# @Date:   2022-09-08 10:54:45
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-12 16:36:59

from pydantic import BaseModel
from typing import Any, Dict, List, Union
from schemas.vertical import DomainPlacementBase
from schemas.catalogue import VSBluePrintInfo, VSDData
from schemas.nst import NST

class AdditionalConf(BaseModel):
    member_vnf_index: str
    primitive: str
    primitive_params: Dict = {}

class CreateVsiData(BaseModel):
    name: str
    description: str
    vsdId: str
    vsiId: str
    domainPlacements: List[DomainPlacementBase] = []
    additionalConf: List[Dict] = []

class RemoveVSIData(BaseModel):
    force: bool

class StatusUpdateData(BaseModel):
    status: Union[str, Dict]

class DomainInfoData(BaseModel):
    domainIds: List


class TenantInfoData(BaseModel):
    username: str
    group: str
    roles: List[str]

class CatalogueInfoData(BaseModel):
    vs_blueprint_info: VSBluePrintInfo
    vsd : VSDData
    nsts: List[NST]
    vsb_actions: List = []


class PlacementInfoData(BaseModel):
    domainId: str
    sliceEnabled: bool
    nsdId: str = None
    nstId: str = None

class InstantiateNsiData(BaseModel):
    name: str
    description: str = None
    domainId: str = None
    nstId: str = None
    additionalConf: AdditionalConf = None

class FecthNsiInfoData(BaseModel):
    domainId: str = None
    nsiId: str = None

class FetchNsInfoData(BaseModel):
    domainId: str = None
    nsId: str = None

class FetchPrimitiveData(BaseModel):
    domainId: str = None
    nfvoId: str
    actionId: str = None

class UpdateResourcesNfvoIdsData(BaseModel):
    componentName: str
    componentId: str
    additionalData: Dict[str, str]

class NsiInfoData(BaseModel):
    nsiId: str
    nsiInfo: str = None

class PrimitiveData(BaseModel):
    primitiveName: str
    primitiveTarget: str
    primitiveInternalTarget: str
    primitiveParams: Dict = {}
    actionId: str

class ActionNsData(BaseModel):
    primitiveName: str = None
    domainId: str
    nsId: str = None
    actionId: str = None # Id given by the Coordinator to identify the Action
    additionalConf: Dict


class ActionResponseData(BaseModel):
    primitiveName: str = None
    actionId: str # Id given by the Coordinator to identify the Action(Primitive)
    nfvoId: str # Id given by the NFVO to identify the Action(Primitive)
    status: str
    output: str

# Message to inform the Coordinator of a update on the Action(Primitive) lifecyle
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
    data: Union[DomainInfoData, CreateVsiData, TenantInfoData,
                CatalogueInfoData, RemoveVSIData, List[PlacementInfoData],
                ActionResponseData,  ActionUpdateData, NsiInfoData, 
                UpdateResourcesNfvoIdsData, PrimitiveData, ActionNsData,
                FetchPrimitiveData, StatusUpdateData, FetchNsInfoData, 
                FecthNsiInfoData] = None
