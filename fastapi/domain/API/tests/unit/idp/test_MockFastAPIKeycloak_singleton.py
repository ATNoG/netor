# @Author: Daniel Gomes
# @Date:   2022-10-31 11:11:40
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-31 11:16:52
from configure_test_idp import MockFastAPIKeycloak


def test_singleton():

    instance_1 = MockFastAPIKeycloak()
    instance_2 = MockFastAPIKeycloak()

    assert instance_1 == instance_2

    instance_1.my_var = 0
    assert instance_1.my_var == 0

    instance_2.my_var = 1
    assert instance_2.my_var == 1

    assert instance_1 == instance_2
    assert instance_1.my_var == 1
    assert instance_2.my_var == 1