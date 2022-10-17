# @Author: Daniel Gomes
# @Date:   2022-09-06 16:20:07
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-07 18:34:48
from typing import List
from pydantic import BaseModel

class Tenant(BaseModel):
    username: str
    group: str
    roles: List[str]
    token: str = None
    @classmethod
    def is_admin(self):
        return "ADMIN" in self.roles


class Token(BaseModel):
    access_token: str
    token_type: str
