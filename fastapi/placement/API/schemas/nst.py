# @Author: Daniel Gomes
# @Date:   2022-09-22 10:13:22
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-25 09:52:24
from __future__ import annotations
from typing import List, Any, Dict
from pydantic import BaseModel


class NSTServiceProfile(BaseModel):
    latency: int
    sST: str
    resource_sharing_level: Any = None
    max_number_of_UEs: int
    coverage_area_TA_list: List = []
    service_profile_id: str
    uRLLC_perf_req: List[Dict] = []
    availability: float
    pLMN_id_list: List = []
    eMBB_perf_req: List[Dict] = []   
    uE_mobility_level: None


class NST(BaseModel):
    nst_name: str
    nsd_version: str
    geographical_area_info_list: List = []
    nst_provider: str
    nsd_id: str = None
    nst_id: str = None
    nst_version: str
    nst_service_profile: NSTServiceProfile
    nsst_type: str
    nsst_ids: List = []
    nsst: List[NST] = []
