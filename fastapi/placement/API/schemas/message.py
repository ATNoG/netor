# @Author: Daniel Gomes
# @Date:   2022-09-08 10:54:45
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-03 00:38:13

from pydantic import BaseModel
from typing import Dict, List, Union
from schemas.catalogue import VSBluePrintInfo, VSDData
from schemas.nst import NST
from schemas.vertical import DomainPlacementBase


class CreateVsiData(BaseModel):
    name: str
    description: str
    vsdId: str
    domainPlacements: List[DomainPlacementBase] = []
    additionalConf: List[Dict] = []


class DomainInfoData(BaseModel):
    domainIds: List


class CatalogueInfoData(BaseModel):
    vs_blueprint_info: VSBluePrintInfo
    vsd: VSDData
    nsts: List[NST]
    vsb_actions: List = []


class TranslationInfoData(BaseModel):
    domainId: str
    sliceEnabled: bool
    nsdId: str = None
    nstId: str = None


class RemoveVSIData(BaseModel):
    force: bool


class Message(BaseModel):
    vsiId: int
    msgType: str = None
    message: str = ""
    error: bool = False
    tenantId: str = None
    data: Union[DomainInfoData, CreateVsiData,
                CatalogueInfoData, RemoveVSIData,
                List[TranslationInfoData]] = None

