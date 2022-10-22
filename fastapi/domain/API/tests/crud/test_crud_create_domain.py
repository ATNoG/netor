# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-20 13:21:56

# general imports
import pytest
from pydantic import ValidationError

# custom imports
from schemas import domain as DomainSchemas
from sql_app.crud import domain as CRUDDomain
from sql_app.database import Base
from configure_test_db import override_get_db
from configure_test_db import engine


# Create the DB before each test and delete it afterwards
@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Tests
def test_simple_domain_database_creation():

    database = next(override_get_db())

    domain = DomainSchemas.DomainCreate(
        domainId="ITAv",
        name="ITAv domain",
        url="http://10.0.10.10",
        interfaceType="HTTP",
        ownedLayers=[]
    )
    
    result = CRUDDomain.createDomain(
        db=database,
        domain_data=domain
    )

    assert CRUDDomain.getDomainById(
        db=database,
        domainId=result.domainId).name == "ITAv domain"


def test_medium_domain_database_creation():

    database = next(override_get_db())

    domain = DomainSchemas.DomainCreate(
        domainId="ITAv",
        name="ITAv domain",
        description="ITAv domain description",
        url="http://10.0.10.10",
        interfaceType="HTTP",
        ownedLayers=[],
        auth=False,
        admin="ITAv",
        owner="admin"
    )

    result = CRUDDomain.createDomain(
        db=database,
        domain_data=domain
    )

    created_domain = CRUDDomain.getDomainById(
        db=database,
        domainId=result.domainId
    )

    assert created_domain.name == "ITAv domain"
    assert created_domain.auth == False
    assert created_domain.owner == "admin"
    assert created_domain.admin == "ITAv"
    assert created_domain.description == "ITAv domain description"


def test_complex_domain_database_creation():

    database = next(override_get_db())
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

    created_domain = CRUDDomain.getDomainById(
        db=database,
        domainId=result.domainId
    )
    assert len(created_domain.ownedLayers) > 0

    assert created_domain.ownedLayers[0].domainLayerId == ownedLayer.domainLayerId
    assert created_domain.ownedLayers[0].domainLayerType == ownedLayer.domainLayerType


def test_error_domain_database_creation():

    with pytest.raises(ValidationError) as exception:
        DomainSchemas.DomainCreate(
            name="ITAv domain",
            description="ITAv domain description",
            interfaceType="HTTP",
            auth=False,
            admin="ITAv",
            owner="admin"
        )
    print(exception)
    assert "domainId" and "url" and "ownedLayers" in str(exception)


def test_error_ownedlayer_database_creation():

    with pytest.raises(ValidationError) as exception:
        DomainSchemas.OwnedLayersCreate(
            domainLayerType="ONAP",
            username="5gasp",
            password="blallalsad",
            project="5gasp",
            vimAccount="Tron"
        )
    print(exception)
    assert "domainLayerId" and "domainLayerType" in str(exception)
