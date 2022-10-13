# @Author: Daniel Gomes
# @Date:   2022-09-25 15:10:39
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-25 15:12:56

class VSDNotFound(Exception):
    def __init__(self, vsd_id=None):
        if vsd_id:
            self.vsd_id = vsd_id
            self.message = f"VSD with Id '{self.vsd_id}' was not found"
        else:
            self.message = "VSD with the Given Id does not exist"
        super().__init__(self.message)

    def __str__(self):
        return self.message