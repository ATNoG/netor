# @Author: Daniel Gomes
# @Date:   2022-10-31 15:17:05
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-01 11:29:45
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
def test_correct_domains_get():
    database = next(override_get_db())
    inject_admin_user()

    domain = DomainSchemas.DomainCreate(
        domainId="ITAv",
        name="ITAv domain",
        url="http://10.0.10.10",
        interfaceType="HTTP",
        ownedLayers=[]
    )
    domain_2 = DomainSchemas.DomainCreate(
        domainId="OdinS",
        name="OdinS domain",
        url="http://20.0.20.20",
        interfaceType="HTTP",
        ownedLayers=[]
    )
    domains = [domain, domain_2]
    _ = [CRUDDomain.createDomain(db=database, domain_data=d)
         for d in domains]
    response = test_client.get(
        "/domains",
    )
    assert response.status_code == 200
    data = response.json()['data']
    assert len(data) == 2
    assert data[0]['domainId'] == domain.domainId
    assert data[0]['name'] == domain.name
    assert data[1]['domainId'] == domain_2.domainId
    assert data[1]['name'] == domain_2.name


def test_unauthorized_domains_get():
    MockOIDCUser().inject_mocked_oidc_user(
        id="1111-1111-1111-1111",
        username="tenant-user",
        roles=[IDP_TENANT_USER]
    )
    response = test_client.get(
               "/domains")
    assert response.status_code == 403
    assert f'Role "{IDP_ADMIN_USER}" is required to perform this '\
           'action' in response.json()['detail']
