# -*- coding: utf-8 -*-
# @Author: Daniel Gomes
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-31 15:04:55

# general imports
import pytest
from aux.constants import IDP_ADMIN_USER, IDP_TENANT_USER
from exceptions.domain import CouldNotAuthenticatetoNFVO
# custom imports
from sql_app.models import Domain
from pytest_mock import MockerFixture

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
def test_correct_domain_post(mocker: MockerFixture):
    # Mock Authentication to OSM Driver
    inject_admin_user()
    # Mock Authentication to OSM Driver
    auth_driver = mocker.patch("driver.driver_osm.OSMDriver.authenticate")
    auth_driver.return_value = True

    response = test_client.post(
        "/domain",
        json={
            "domainId": "ITAV",
            "admin": "ITAV",
            "description": "ITAV domain",
            "auth": False,
            "interfaceType": "HTTP",
            "url": "http://10.0.10.0",
            "name": "ITAV domain",
            "owner": "ITAV domain",
            "ownedLayers": [
                {
                    "domainLayerId": "ITAV_OSM",
                    "domainLayerType": "OSM_NSP",
                    "username": "5gasp",
                    "password": "passwd",
                    "project": "5gasp",
                    "vimAccount": "Tron"
                }
            ]
        }
    )
    assert response.status_code == 201
    assert response.json()['data'] != {}
    data = response.json()['data']
    assert auth_driver.called
    assert data['domainId'] == "ITAV"
    assert data['name'] == "ITAV domain"
    assert data['url'] == 'http://10.0.10.0'


def test_unauthorized_domain_post(mocker: MockerFixture):
    # Mock Authentication to OSM Driver
    # Prepare Mocked OIDC User
    MockOIDCUser().inject_mocked_oidc_user(
        id="1111-1111-1111-1111",
        username="tenant-user",
        roles=[IDP_TENANT_USER]
    )

    response = test_client.post(
        "/domain",
        json={
            "domainId": "ITAV",
            "admin": "ITAV",
            "description": "ITAV domain",
            "auth": False,
            "interfaceType": "HTTP",
            "url": "http://10.0.10.0",
            "name": "ITAV domain",
            "owner": "ITAV domain",
            "ownedLayers": [
                {
                    "domainLayerId": "ITAV_OSM",
                    "domainLayerType": "OSM_NSP",
                    "username": "5gasp",
                    "password": "passwd",
                    "project": "5gasp",
                    "vimAccount": "Tron"
                }
            ]
        }
    )
    assert response.status_code == 403
    assert f'Role "{IDP_ADMIN_USER}" is required to perform this '\
        'action' in response.json()['detail']


def test_incorrect_nfvo_post(mocker: MockerFixture):
    auth_driver = mocker.patch("driver.driver_osm.OSMDriver.authenticate")
    auth_driver.side_effect = CouldNotAuthenticatetoNFVO()
    inject_admin_user()
    response = test_client.post(
        "/domain",
        json={
            "domainId": "ITAV",
            "admin": "ITAV",
            "description": "ITAV domain",
            "auth": False,
            "interfaceType": "HTTP",
            "url": "http://10.0.10.0",
            "name": "ITAV domain",
            "owner": "ITAV domain",
            "ownedLayers": [
                {
                    "domainLayerId": "ITAV_OSM",
                    "domainLayerType": "OSM_NSP",
                    "username": "5gasp",
                    "password": "wrong_password",
                    "project": "5gasp",
                    "vimAccount": "Tron"
                }
            ]
        }
    )
    assert response.status_code == 400
    assert not response.json()['success']
    assert auth_driver.call_count == 1
    assert any("Could not Authenticate to the NFVO" in x
               for x in response.json()['errors'])


def test_incorrect_domain_data_post(mocker: MockerFixture):
    database = next(override_get_db())

    # add sample object to db
    domain_db = Domain(
            domainId="ITAV",
            admin="ITAV",
            description="ITAV domain description",
            auth=False,
            interfaceType="HTTP",
            url="http://10.0.10.0",
            name="ITAV domain",
            owner="ITAV domain")
    database.add(domain_db)
    database.commit()
    inject_admin_user()
    response = test_client.post(
        "/domain",
        json={
            "domainId": "ITAV",
            "admin": "ITAV",
            "description": "ITAV domain description",
            "auth": False,
            "interfaceType": "HTTP",
            "url": "http://10.0.10.0",
            "name": "ITAV domain",
            "owner": "ITAV domain",
            "ownedLayers": [
                {
                    "domainLayerId": "ITAV_OSM",
                    "domainLayerType": "OSM_NSP",
                    "username": "5gasp",
                    "password": "wrong_password",
                    "project": "5gasp",
                    "vimAccount": "Tron"
                }
            ]
        }
    )
    print(response.json())
    assert response.status_code == 400
    assert not response.json()['success']
    assert any("already exists" in x
               for x in response.json()['errors'])
