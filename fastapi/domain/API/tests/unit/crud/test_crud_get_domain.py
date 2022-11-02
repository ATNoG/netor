# -*- coding: utf-8 -*-
# @Author: Daniel Gomes
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-01 16:01:36

# general imports
import pytest

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
def test_get_domain_by_id():

    database = next(override_get_db())

    domain = DomainSchemas.DomainCreate(
        domainId="ITAv",
        name="ITAv domain",
        url="http://10.0.10.10",
        interfaceType="HTTP",
        ownedLayers=[]
    )
    db_domain = CRUDDomain.createDomain(
        db=database,
        domain_data=domain
    )
    result_retrieved = CRUDDomain.getDomainById(db=database,
                                                domainId=db_domain.domainId)

    assert result_retrieved.domainId == domain.domainId
    assert result_retrieved.name == domain.name
    assert result_retrieved.url == domain.url


def test_get_non_existent_domain():

    database = next(override_get_db())
 
    created_domain = CRUDDomain.getDomainById(
        db=database,
        domainId="ITAV"
    )

    assert created_domain is None
