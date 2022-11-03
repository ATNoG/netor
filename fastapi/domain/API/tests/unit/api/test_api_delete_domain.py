# @Author: Daniel Gomes
# @Date:   2022-11-01 23:34:15
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-01 23:52:25
import pytest
from aux.constants import IDP_ADMIN_USER, IDP_TENANT_USER
from exceptions.domain import CouldNotAuthenticatetoNFVO
# custom imports
import schemas.domain as DomainSchemas
import sql_app.crud.domain as CRUDDomain
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


## store in DB 
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

    