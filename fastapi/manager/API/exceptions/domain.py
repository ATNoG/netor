# @Author: Daniel Gomes
# @Date:   2022-09-19 17:08:20
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-19 17:09:25


class DomainNotFound(Exception):
    def __init__(self, domain_id=None):
        if domain_id:
            self.domain_id = domain_id
            self.message = f"Domain with Id '{self.domain_id}' was not found"
        else:
            self.message = "Domain with the Given Id does not exist"
        super().__init__(self.message)

    def __str__(self):
        return self.message
