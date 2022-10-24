# -*- coding: utf-8 -*-
# @Author: Daniel Gomes
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-24 11:47:43

# general imports
import pytest
from exceptions.domain import CouldNotAuthenticatetoNFVO
# custom imports
from sql_app.models import Domain
from configure_test_db import engine
from configure_test_db import test_client
from sql_app.database import Base
from configure_test_db import override_get_db
from configure_test_db import engine
from pytest_mock import MockerFixture

# Create the DB before each test and delete it afterwards
@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Tests
def test_correct_domain_post(mocker: MockerFixture):
    # Mock Authentication to OSM Driver
    auth_driver = mocker.patch("driver.driver_osm.OSMDriver.authenticate")
    auth_driver.return_value= True
    
    token = "mytoken"
    response = test_client.post(
        "/domain",
        headers={'Authorization': f'Bearer {token}'},
        json={
            "domainId":"ITAV",
            "admin":"ITAV",
            "description":"ITAV domain",
            "auth": False,
            "interfaceType":"HTTP",
            "url":"http://10.0.10.0",
            "name":"ITAV domain",
            "owner":"ITAV domain",
            "ownedLayers":[
                {
                    "domainLayerId":"ITAV_OSM",
                    "domainLayerType":"OSM_NSP",
                    "username":"5gasp",
                    "password":"passwd",
                    "project":"5gasp",
                    "vimAccount":"Tron"
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


def test_incorrect_nfvo_post(mocker: MockerFixture):
    auth_driver = mocker.patch("driver.driver_osm.OSMDriver.authenticate")
    auth_driver.side_effect = CouldNotAuthenticatetoNFVO()
    token = "mytoken"
    response = test_client.post(
        "/domain",
        headers={'Authorization': f'Bearer {token}'},
        json={
            "domainId":"ITAV",
            "admin":"ITAV",
            "description":"ITAV domain",
            "auth": False,
            "interfaceType":"HTTP",
            "url":"http://10.0.10.0",
            "name":"ITAV domain",
            "owner":"ITAV domain",
            "ownedLayers":[
                {
                    "domainLayerId":"ITAV_OSM",
                    "domainLayerType":"OSM_NSP",
                    "username":"5gasp",
                    "password":"wrong_password",
                    "project":"5gasp",
                    "vimAccount":"Tron"
                }
            ]
        }
    )
    assert response.status_code == 400
    assert response.json()['success'] == False
    assert auth_driver.call_count == 1
    assert any("Could not Authenticate to the NFVO" in x \
                   for x in response.json()['errors'])


def test_incorrect_domain_data_post(mocker: MockerFixture):
    database = next(override_get_db())
    token = "mytoken"
    # add sample object to db
    domain_db = Domain(domainId="ITAV",
            admin="ITAV",
            description="ITAV domain description",
            auth=False,
            interfaceType="HTTP",
            url="http://10.0.10.0",
            name="ITAV domain",
            owner="ITAV domain")
    database.add(domain_db)
    database.commit()
    response = test_client.post(
        "/domain",
        headers={'Authorization': f'Bearer {token}'},
        json={
            "domainId":"ITAV",
            "admin":"ITAV",
            "description":"ITAV domain description",
            "auth": False,
            "interfaceType":"HTTP",
            "url":"http://10.0.10.0",
            "name":"ITAV domain",
            "owner":"ITAV domain",
            "ownedLayers":[
                {
                    "domainLayerId":"ITAV_OSM",
                    "domainLayerType":"OSM_NSP",
                    "username":"5gasp",
                    "password":"wrong_password",
                    "project":"5gasp",
                    "vimAccount":"Tron"
                }
            ]
        }
    )
    print(response.json())
    assert response.status_code == 400
    assert response.json()['success'] == False
    assert any("already exists" in x \
                   for x in response.json()['errors'])
  