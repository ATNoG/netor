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
    latency: int = None
    sST: str = None
    resource_sharing_level: Any = None
    max_number_of_UEs: int = None
    coverage_area_TA_list: List = []
    service_profile_id: str = None
    uRLLC_perf_req: List[Dict] = []
    availability: float = None
    pLMN_id_list: List = []
    eMBB_perf_req: List[Dict] = []   
    uE_mobility_level: Any = None


class NST(BaseModel):
    nst_name: str  = None
    nsd_version: str = None
    geographical_area_info_list: List = []
    nst_provider: str
    nsd_id: str = None
    nst_id: str = None
    nst_version: str
    nst_service_profile: NSTServiceProfile = None
    nsst_type: str = None
    nsst_ids: List = []
    nsst: List[NST] = []
