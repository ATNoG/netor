# @Author: Daniel Gomes
# @Date:   2022-09-07 17:11:07
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-07 10:23:58
from pydantic import BaseModel, validator
from typing import List, Optional, Dict


class ComponentConfigs(BaseModel):
    domainPlacementId: int = None
    componentName: str
    conf: Dict


class DomainPlacementBase(BaseModel):
    domainId: str
    componentName: str


class DomainPlacementCreate(DomainPlacementBase):
    pass


class DomainPlacement(DomainPlacementBase):
    domainPlacementId: int


class VSIBase(BaseModel):
    description: str
    name: str
    vsdId: str
    domainPlacements: List[DomainPlacementBase]
    additionalConf: List[ComponentConfigs]


class VSICreate(VSIBase):
    domainPlacements: List[DomainPlacementCreate]

    @validator('domainPlacements', 'additionalConf')
    def verify_component_names(cls, values):
        if values:
            print("VALUES", values)
            check_naming = [v.componentName for v in values]
            if len(set(check_naming)) != len(check_naming):
                raise ValueError('The Component Names must be different')
        return values


class VSI(VSIBase):
    vsiId: int
    statusMessage: Optional[str] = None
    altitude: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radioRange: Optional[float] = None
    mappedInstanceId: str
    ranEndPointId: Optional[str] = None
    status: str
    domainPlacements: List[DomainPlacement]
    # TODO: Return remaining info
