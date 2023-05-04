
from pydantic import BaseModel

class PrimitiveStatus(BaseModel):
    actionId: str = None
    domainId: str = None
    nfvoId: str = None # id of the operation given by the nfvo
    isAlarm: bool = False # Flag to identify the Alarm Day-2 Actions
    status: str = None
    output: str = None
    
class ServiceComposition(BaseModel):
    sliceEnabled: bool = None
    domainId: str = None
    nfvoId: str = None
    status: str