# @Author: Daniel Gomes
# @Date:   2022-10-22 09:41:24
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-31 15:12:27


# general imports
import pytest
# custom imports
from aux.constants import IDP_ADMIN_USER, IDP_TENANT_USER
import schemas.domain as DomainSchemas
import sql_app.crud.domain as CRUDDomain
from configure_test_idp import (
    inject_admin_user,
    setup_test_idp,
    MockOIDCUser
)


def import_modules():
    # additional custom imports
    from configure_test_db import (
        engine as imported_engine,
        test_client as imported_test_client,
        override_get_db as imported_override_get_db
    )
    from sql_app.database import Base as imported_base
    global engine
    engine = imported_engine
    global Base
    Base = imported_base
    global test_client
    test_client = imported_test_client
    global override_get_db
    override_get_db = imported_override_get_db


# Create the DB before each test and delete it afterwards
@pytest.fixture(autouse=True)
def setup(monkeypatch, mocker):
    # Setup Test IDP.
    # This is required before loading the other modules
    setup_test_idp(monkeypatch, mocker)
    import_modules()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Tests
def test_correct_domain_get():
    database = next(override_get_db())
    inject_admin_user()

    domain = DomainSchemas.DomainCreate(
        domainId="ITAv",
        name="ITAv domain",
        url="http://10.0.10.10",
        interfaceType="HTTP",
        ownedLayers=[]
    )

    CRUDDomain.createDomain(
        db=database,
        domain_data=domain)

    response = test_client.get(
        f"/domain/{domain.domainId}",
    )
    assert response.status_code == 200
    data = response.json()['data']
    assert data['domainId'] == domain.domainId
    assert data['name'] == domain.name
    assert data['url'] == domain.url


def test_non_existent_domain_get():
    inject_admin_user()
    domainId = "ITAV"
    response = test_client.get(
        f"/domain/{domainId}",
    )
    assert response.status_code == 400
    assert not response.json()['success']
    error_msg = f"Domain with Id '{domainId}' was not found"
    assert any(error_msg in x
               for x in response.json()['errors'])


def test_non_authorized_domain_get():
    MockOIDCUser().inject_mocked_oidc_user(
        id="1111-1111-1111-1111",
        username="tenant-user",
        roles=[IDP_TENANT_USER]
    )
    domainId = "ITAV"
    response = test_client.get(
        f"/domain/{domainId}")
    assert response.status_code == 403
    assert f'Role "{IDP_ADMIN_USER}" is required to perform this '\
           'action' in response.json()['detail']
