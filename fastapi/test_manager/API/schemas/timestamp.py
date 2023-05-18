# @Author: Daniel Gomes
# @Date:   2022-11-12 08:44:47
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-12 10:51:11

from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime


class TimestampData(BaseModel):
    action: str
    timestamp: datetime
    domain: str = None


class Steps(BaseModel):
    action: str
    timestamp: str


class FileData(BaseModel):
    netor_initial_step: Steps = None
    alarm_step: Steps = None
    remaining_steps: Dict[str, List[Steps]] = {}


