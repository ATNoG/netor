# @Author: Daniel Gomes
# @Date:   2022-09-07 17:57:57
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-03 09:39:22

class VerticalAlreadyExists(Exception):
    def __init__(self, vs_id=None):
        if vs_id:
            self.vs_id = vs_id
            self.message = f"Vertical with Id '{self.vs_id}' already exists"
        else:
            self.message = "Vertical with Id already exists"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class VerticalNotFound(Exception):
    def __init__(self, vs_id=None):
        if vs_id:
            self.vs_id = vs_id
            self.message = f"Vertical with Id '{self.vs_id}' was not found"
        else:
            self.message = "Vertical with the Given Id does not exist"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InvalidComponentName(Exception):
    def __init__(self):
        self.message = "Components should have the same naming and number"
        super().__init__(self.message)

    def __str__(self):
        return self.message
