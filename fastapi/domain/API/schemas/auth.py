# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-29 10:51:24

# generic imports
from typing import List
from pydantic import BaseModel


class Tenant(BaseModel):
    username: str
    group: str
    roles: List[str]


class Token(BaseModel):
    access_token: str
    token_type: str
