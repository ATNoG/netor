# -*- coding: utf-8 -*-
# @Author: Daniel Gomes
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-01 16:05:03

# general imports
import pytest
from pydantic import ValidationError

# custom imports
from schemas import domain as DomainSchemas
from sql_app.crud import domain as CRUDDomain
from configure_test_idp import (
    setup_test_idp,
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
    assert not created_domain.auth
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
    _layer = created_domain.ownedLayers[0]
    assert _layer.domainLayerId == ownedLayer.domainLayerId
    assert _layer.domainLayerType == ownedLayer.domainLayerType


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
