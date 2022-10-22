# @Author: Daniel Gomes
# @Date:   2022-10-22 09:41:24
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-22 09:51:33


# general imports
import pytest
# custom imports
import schemas.domain as DomainSchemas
import sql_app.crud.domain as CRUDDomain
from configure_test_db import engine
from configure_test_db import test_client
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
def test_correct_domain_get():
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
        domain_data=domain)
    token = "mytoken"
    response = test_client.get(
        f"/domain/{domain.domainId}",
        headers={'Authorization': f'Bearer {token}'}    
    )
    assert response.status_code == 200
    data = response.json()['data']
    assert data['domainId'] == domain.domainId
    assert data['name'] == domain.name
    assert data['url'] == domain.url
    
