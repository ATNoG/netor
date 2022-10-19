# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-18 14:34:32

# general imports
import pytest
from pydantic import ValidationError
import datetime

# custom imports
from database.crud import crud
import schemas.tmf632_party_mgmt as TMF632Schemas
from tests.configure_test_db import override_get_db
from tests.configure_test_db import engine
from database.database import Base


# Create the DB before each test and delete it afterwards
@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Tests
def test_simple_organization_database_creation():

    database = next(override_get_db())

    organization = TMF632Schemas.OrganizationCreate(
        tradingName="ITAv"
    )

    result = crud.create_organization(
        db=database,
        organization=organization
    )

    assert crud.get_organization_by_id(
        db=database,
        id=result.id).tradingName == "ITAv"


def test_medium_organization_database_creation():

    database = next(override_get_db())

    organization = TMF632Schemas.OrganizationCreate(
        tradingName="ITAv",
        isHeadOffice=True,
        isLegalEntity=True,
        name="ITAv's Testbed",
        organizationType="Testbed",
    )

    result = crud.create_organization(
        db=database,
        organization=organization
    )

    created_organization = crud.get_organization_by_id(
        db=database,
        id=result.id
    )

    assert created_organization.tradingName == "ITAv"
    assert created_organization.isHeadOffice
    assert created_organization.isLegalEntity
    assert created_organization.name == "ITAv's Testbed"
    assert created_organization.organizationType == "Testbed"


def test_complex_organization_database_creation():

    database = next(override_get_db())

    organization = TMF632Schemas.OrganizationCreate(
        tradingName="ITAv",
        isHeadOffice=True,
        isLegalEntity=True,
        name="ITAv's Testbed",
        organizationType="Testbed",
        existsDuring=TMF632Schemas.TimePeriod(
            startDateTime="2015-10-22T08:31:52.026Z",
            endDateTime="2016-10-22T08:31:52.026Z",
        ),
        status="validated"
    )

    result = crud.create_organization(
        db=database,
        organization=organization
    )

    created_organization = crud.get_organization_by_id(
        db=database,
        id=result.id
    )

    startDateTime = datetime.datetime(2015, 10, 22, 8, 31, 52, 26000)
    endDateTime = datetime.datetime(2016, 10, 22, 8, 31, 52, 26000)

    assert created_organization.existsDuring\
        .startDateTime.replace(tzinfo=None) == startDateTime
    assert created_organization.existsDuring\
        .endDateTime.replace(tzinfo=None) == endDateTime


def test_error_organization_database_creation():

    with pytest.raises(ValidationError) as exception:
        TMF632Schemas.OrganizationCreate(
            tradingName="ITAv",
            isHeadOffice=True,
            isLegalEntity=True,
            name="ITAv's Testbed",
            organizationType="Testbed",
            existsDuring=TMF632Schemas.TimePeriod(
                startDateTime="2015-10-22T08:31:52.026Z",
                endDateTime="2016-10-22T08:31:52.026Z",
            ),
            status="BAD_STATUS"
        )
    print(exception)
    assert "OrganizationCreate" and "validated" and "initialized" and "closed"\
        in str(exception)