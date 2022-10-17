# @Author: Daniel Gomes
# @Date:   2022-09-01 17:01:13
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-01 17:02:13
from pydantic import BaseModel


class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    pass