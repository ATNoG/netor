# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-22 09:38:44

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
