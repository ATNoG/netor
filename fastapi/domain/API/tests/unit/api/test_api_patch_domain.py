# @Author: Daniel Gomes
# @Date:   2022-11-01 11:30:44
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-01 15:50:02

# general imports
import pytest
# custom imports
from aux.constants import IDP_ADMIN_USER, IDP_TENANT_USER
from pytest_mock import MockerFixture
from exceptions.domain import CouldNotAuthenticatetoNFVO
import schemas.domain as DomainSchemas
import sql_app.crud.domain as CRUDDomain
from configure_test_idp import (
    inject_admin_user,
    setup_test_idp,
    MockOIDCUser
)


def create_domain(database):
    ownedLayer = DomainSchemas.OwnedLayersCreate(
        domainLayerId="ITAV_OSM",
        domainLayerType="OSM_NSP",
        username="5gasp",
        password="blallalsad",
        project="5gasp",
        vimAccount="Tron"
    )
    domain = DomainSchemas.DomainCreate(
        domainId="ITAv",
        name="ITAv domain",
        description="ITAv domain description",
        url="http://10.0.10.10",
        interfaceType="HTTP",
        ownedLayers=[ownedLayer],
        auth=False,
        admin="ITAv",
        owner="admin"
    )

    result = CRUDDomain.createDomain(
        db=database,
        domain_data=domain
    )
    return result


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


def test_patch_correct_domain(mocker: MockerFixture):
    inject_admin_user()
    # Mock Authentication to OSM Driver
    auth_driver = mocker.patch("driver.driver_osm.OSMDriver.authenticate")
    auth_driver.return_value = True
    domainId = "ITAv"
    database = next(override_get_db())
    result = create_domain(database)
    response = test_client.patch(
        f"/domain/{domainId}",
        json={
            "admin": "ITAv",
            "description": "ITAv new domain description",
            "auth": False,
            "interfaceType": "HTTP",
            "url": "http://10.0.10.0",
            "name": "ITAv domain",
            "owner": "ITAv domain",
            "ownedLayers": [
                {
                    "domainLayerId": "ITAV_OSM",
                    "domainLayerType": "OSM_NSP",
                    "username": "5gasp",
                    "password": "newpasswd",
                    "project": "5gasp",
                    "vimAccount": "NewTron"
                }
            ]
        }
    )
    assert response.status_code == 200
    assert response.json()['data'] != {}
    data = response.json()['data']
    assert auth_driver.called
    assert data['domainId'] == result.domainId
    assert data['description'] != result.description
    assert len(data['ownedLayers']) == 1
    layer = data['ownedLayers'][0]
    assert layer['domainLayerId'] == result.ownedLayers[0].domainLayerId
    assert layer['vimAccount'] == result.ownedLayers[0].vimAccount
    assert 'password' not in layer


def test_patch_non_existent_domain(mocker: MockerFixture):
    domainId = "ITAv"
    inject_admin_user()
    response = test_client.patch(
        f"/domain/{domainId}",
        json={
            "admin": "ITAv",
            "description": "ITAv new domain description",
            "auth": False,
            "interfaceType": "HTTP",
            "url": "http://10.0.10.0",
            "name": "ITAv domain",
            "owner": "ITAv domain",
            "ownedLayers": [
                {
                    "domainLayerId": "ITAV_OSM",
                    "domainLayerType": "OSM_NSP",
                    "username": "5gasp",
                    "password": "newpasswd",
                    "project": "5gasp",
                    "vimAccount": "NewTron"
                }
            ]
        }
    )
    assert response.status_code == 400
    assert not response.json()['success']
    assert any(f"Domain with Id '{domainId}' was not found" in x
               for x in response.json()['errors'])


def test_patch_incorrect_domain_nfvo_data(mocker: MockerFixture):
    inject_admin_user()
    # Mock Authentication to OSM Driver
    auth_driver = mocker.patch("driver.driver_osm.OSMDriver.authenticate")
    auth_driver.side_effect = CouldNotAuthenticatetoNFVO()
    domainId = "ITAv"
    database = next(override_get_db())
    create_domain(database)
    response = test_client.patch(
        f"/domain/{domainId}",
        json={
            "admin": "ITAv",
            "description": "ITAv new domain description",
            "auth": False,
            "interfaceType": "HTTP",
            "url": "http://10.0.10.0",
            "name": "ITAv domain",
            "owner": "ITAv domain",
            "ownedLayers": [
                {
                    "domainLayerId": "ITAV_ONAP",
                    "domainLayerType": "OSM_NSP",
                    "username": "5gasp",
                    "password": "wrong_password",
                    "project": "5gasp",
                    "vimAccount": "NewTron"
                }
            ]
        }
    )
    assert auth_driver.call_count == 1
    assert not response.json()['success']
    assert any("Could not Authenticate to the NFVO" in x
               for x in response.json()['errors'])


def test_unauthorized_domain_patch(mocker: MockerFixture):
    domainId = "ITAv"
    MockOIDCUser().inject_mocked_oidc_user(
        id="1111-1111-1111-1111",
        username="tenant-user",
        roles=[IDP_TENANT_USER]
    )
    response = test_client.patch(
        f"/domain/{domainId}",
        json={
            "admin": "ITAv",
            "description": "ITAv new domain description",
            "auth": False,
            "interfaceType": "HTTP",
            "url": "http://10.0.10.0",
            "name": "ITAv domain",
            "owner": "ITAv domain",
            "ownedLayers": [
                {
                    "domainLayerId": "ITAV_ONAP",
                    "domainLayerType": "OSM_NSP",
                    "username": "5gasp",
                    "password": "newpasswd",
                    "project": "5gasp",
                    "vimAccount": "NewTron"
                }
            ]
        }
    )

    assert response.status_code == 403
    assert f'Role "{IDP_ADMIN_USER}" is required to perform this '\
        'action' in response.json()['detail']
