

from pydantic import BaseModel
from typing import Union, Dict


class NotifyDetailsData(BaseModel):
    alarm_uuid: str
    description: str = None
    severity: str
    status: str
    operation: str
    threshold_value: float
    metric_name: str
    tags: Dict
    extra_labels: Dict = {}
    start_date: str
    update_date: str = None
    cancel_date: str = None


class LinkAlarmData(BaseModel):
   
    schema_version: str
    schema_type: str
    notify_details: NotifyDetailsData
    actionId: str = None # Useful to identify the action to be applied


class LinkData(BaseModel):
    src_ip: str
    dest_ip: str
    alarm_payload: LinkAlarmData
    
