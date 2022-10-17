# @Author: Daniel Gomes
# @Date:   2022-08-18 14:33:17
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-23 11:30:39


class DomainDriver:
    def __init__(self, host, username, password, project) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.project = project
        self.token = None

    def authenticate(self):
        pass