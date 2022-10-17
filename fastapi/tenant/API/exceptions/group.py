# @Author: Daniel Gomes
# @Date:   2022-08-23 18:29:48
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-01 17:06:22
class GroupNotFound(Exception):
    def __init__(self, group=None):
        if group:
            self.group = group
            self.message = f'Group with name {self.group} doesn\'t exist'
        else:
            self.message = 'Group doesn\'t exist'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class GroupAlreadyExists(Exception):
    def __init__(self, group=None):
        if group:
            self.group = group
            self.message = f'Group with name {self.group} already exists'
        else:
            self.message = 'Group already exists'
        super().__init__(self.message)

    def __str__(self):
        return self.message