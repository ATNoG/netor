# @Author: Daniel Gomes
# @Date:   2022-09-28 10:54:59
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-12 16:47:15

from enum import Enum, unique


@unique
class VSIStatus(Enum):
    CREATED = "1"
    INSTATIATING = "2"
    INSTANTIATED = "3"
    DELETED = "4"

    def __str__(self):
        return str(self.value)


@unique
class ActionStatus(Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    def __str__(self):
        return str(self.value)