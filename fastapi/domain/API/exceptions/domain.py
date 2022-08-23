# @Author: Daniel Gomes
# @Date:   2022-08-18 11:18:47
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-23 11:31:44


class DomainAlreadyExists(Exception):
    def __init__(self, domain_id=None):
        if domain_id:
            self.domain_id = domain_id
            self.message = f"Domain with Id '{self.domain_id}' already exists"
        else:
            self.message = "Domain with Id already exists"
        super().__init__(self.message)

    def __str__(self):
        return self.message


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


class DomainLayerAlreadyExists(Exception):
    def __init__(self, layer_id=None):
        if layer_id:
            self.layer_id = layer_id
            self.message = f"Domain Layer with Id '{self.layer_id}'" \
                           + "already exists"
        else:
            self.message = "Domain with Id already exists"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class CouldNotAuthenticatetoNFVO(Exception):
    def __init__(self):
        self.message = "Could not Authenticate to the NFVO using" \
                       + "the provided credentials"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class DomainLayerTypeNotSupported(Exception):
    def __init__(self, layer_type=None):
        if layer_type:
            self.layer_type = layer_type
            self.message = f"The Domain Layer with type '{self.layer_type}'" \
                + "is not supported"
        else:
            self.message = "The Domain Layer provided is not supported"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class DomainLayersCouldNotBeFound(Exception):
    def __init__(self, layer_id=None):
        if layer_id:
            self.layer_id = layer_id
            self.message = "No Domain Layers could be found for Domain with"\
                           + f" id '{self.layer_id}' already exists"
        else:
            self.message = "Domain with Id already exists"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class DomainDriverNotFound(Exception):
    def __init__(self) -> None:
        self.message = "No NFVO Driver could be found"
        super().__init__(self.message)

    def __str__(self):
        return self.message
