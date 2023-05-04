# @Author: Daniel Gomes
# @Date:   2022-09-22 09:34:33
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-28 13:59:17
from typing import List, Any
from pydantic import BaseModel, validator

from schemas.nst import NST


def parse_correct_type(cls, v, values, **kwargs):
    if (type(v) == str):
        if v.replace('.', '', 1).isdigit():
            return int(v) if '.' in v else float(v)
    return v

class VSDData(BaseModel):
    tenant_id: str
    associated_vsd_id: str = None
    domain_id: str
    vs_descriptor_id: str
    version: str
    is_public: bool = True
    nested_vsd_ids: dict = {}
    service_constraints: List = []
    vs_blueprint_id: str
    name: str
    sla: Any = None
    management_type: str
    qos_parameters: dict

class ParameterData(BaseModel):
    parameter_id: str
    parameter_type: str
    applicability_field: str
    parameter_name: str
    parameter_description: str = None

    @validator('parameter_type')
    def validate_parameter_type(cls, v):
        if v not in ['number']:
            raise ValueError('Not a valid parameter type')
        return v


class InputParameter(BaseModel):
    parameter_id: str
    max_value: Any
    min_value: Any
    # _parse_max_value = validator('max_value',
    #  allow_reuse=True, always=True, pre=True)(parse_correct_type)
   
    # _parse_min_value = validator('min_value',
    #  allow_reuse=True, always=True, pre=True)(parse_correct_type)



class TranslationRules(BaseModel):
    nsd_version: str
    input: List[InputParameter] = []
    nsd_id: str = None
    nst_id: str = None
    blueprint_id: str
    nsd_info_id: str = None
    ns_instantiation_level_id: str = None
    ns_flavour_id: str = None
    
    # @validator('input', each_item=True, pre=True)
    # def validate_input_parameter(cls, v, k):
    #     if v['max_value'] > 


class VSBluePrint(BaseModel):
    urllc_service_category: Any = None
    end_points: List = []
    inter_site: bool = True
    parameters: List[ParameterData] = []
    version: str
    blueprint_id: str
    service_sequence: List = []
    translation_rules: List[TranslationRules]
    name: str
    description: None
    atomic_components: List = []
    configurable_parameters: List = []
    application_metrics: List = []
    connectivity_services: List = []
    embb_service_category: str
    slice_service_type: str
               
class VSBluePrintInfo(BaseModel):
    vs_blueprint: VSBluePrint
    on_boarded_nst_info_id: List = []
    on_boarded_mec_app_package_info_id: List = []
    on_boarded_vnf_package_info_id: List = []
    owner: None
    active_vsd_id: List
    vs_blueprint_id: str
    name: str
    vs_blueprint_version: str
    on_boarded_nsd_info_id: List = []


class CatalogueInfoTranslation(BaseModel):
    vs_blueprint_info: VSBluePrintInfo
    vsd : VSDData
    nsts: List[NST]
    vsb_actions: List = []
