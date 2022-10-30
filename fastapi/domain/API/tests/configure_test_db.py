# @Author: Daniel Gomes
# @Date:   2022-10-18 14:31:04
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-29 14:36:10
from fastapi import HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from schemas.auth import Tenant
# custom imports
from main import app, get_db
from aux.utils import rbacencforcer
from routers import domain as domain_router 
from aux.auth import oauth2_scheme
engine = create_engine(
    url="sqlite:///./test.db",
    connect_args={
        "check_same_thread": False
    }
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_oauth2_scheme(token: str):
    print("ttt", token)
    return token

def override_rbac_enforcer(token:str = Depends(oauth2_scheme)):
    print(token)
    if token == 'mytoken':
        userdata = Tenant(username="admin", roles=["ADMIN"])
        return userdata
    raise HTTPException(
            status_code=400,
            detail="Insufficient permissions to access this resource")

app.dependency_overrides[rbacencforcer] = override_rbac_enforcer
app.dependency_overrides[domain_router.get_db] = override_get_db
app.dependency_overrides[get_db] = override_get_db
test_client = TestClient(app)