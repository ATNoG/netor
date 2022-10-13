# @Author: Daniel Gomes
# @Date:   2022-08-23 14:37:01
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-08 11:36:43
from datetime import timedelta
from fastapi import Depends
# generic imports
from fastapi import APIRouter
from exceptions.auth import NotEnoughPrivileges, TenantDoesNotExist
from sql_app.database import SessionLocal
from sqlalchemy.orm import Session
import logging
import inspect
import sys
import os
import sql_app.crud.auth as CRUD_Auth
from aux import auth
from aux import constants as Constants
import schemas.auth as AuthSchemas

# custom imports
import aux.utils as Utils

# import from parent directory
currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


# Logger
logging.basicConfig(
    format="%(module)-20s:%(levelname)-15s| %(message)s",
    level=logging.INFO
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.post(
    "/oauth/login",
    tags=["auth"],
    summary="Login and get the authentication token",
    description="This endpoint allows the user to login and get the token.",
)
def login_for_access_token(form_data: AuthSchemas.TenantLogin,
                           db: Session = Depends(get_db)):
    try:
        tenant = CRUD_Auth.authenticate_user(
            db, form_data.username, form_data.password)
        access_token_expires = timedelta(
            minutes=Constants.ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = auth.create_access_token(
            data={"sub": tenant.username}, expires_delta=access_token_expires
        )
        return Utils.create_response(
            status_code=200, success=True,
            data={"access_token": access_token, "token_type": "Bearer Token"})
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )

@router.get(
    "/oauth/validate/",
    tags=["auth"],
    summary="Get Tenant information",
    description="This endpoint allows the tenant to get his own information.",
)
def get_my_information(token: str = Depends(auth.oauth2_scheme),
                       db: Session = Depends(get_db)):
    try:
        username = auth.get_current_user(token)
        user_info = CRUD_Auth.get_user_info(db, username)
        return Utils.create_response(status_code=200,
                                     success=True,
                                     data={"user_info": user_info.dict()})
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )


@router.post(
     "/tenant",
    tags=["tenant"],
    summary="Create a Tenant",
    description="This endpoint allows the creation of a Tenant"
)
@Utils.rbac_enforcer(['ADMIN'])
def create_tenant(
                  tenant_in: AuthSchemas.TenantCreate,
                  token: str = Depends(auth.oauth2_scheme),
                  db: Session = Depends(get_db)):
    try:
        tenant = CRUD_Auth.register_tenant(db, tenant_in)
        return Utils.create_response(status_code=200,
                                     success=True,
                                     data=tenant.as_dict())
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        ) 

@router.get(
    "/tenant/{tenant_username}",
    tags=["tenant"],
    summary="Get a tenant by its Username",
    description="This endpoint allows getting Tenant's Info"
)
@Utils.rbac_enforcer(['ADMIN', 'TENANT'])
def get_tenant_by_id(tenant_username: str,
                     token: str = Depends(auth.oauth2_scheme),
                     db: Session = Depends(get_db)):
    try:
        tenant = CRUD_Auth.getTenantByUsername(db, tenant_username)
        if not tenant:
            raise TenantDoesNotExist(tenant)
        current_user = auth.get_current_user(token)
        if current_user != tenant_username:
            raise NotEnoughPrivileges(current_user)
        tenant = CRUD_Auth.get_user_info(db, tenant_username).dict()
        return Utils.create_response(status_code=200,
                                     success=True,
                                     data=tenant)
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )

@router.get(
    "/tenant",
    tags=["tenant"],
    summary="Get all tenants",
    description="This endpoint allows getting all Tenants Info"
)
@Utils.rbac_enforcer(['ADMIN'])
def get_tenant_by_id(
                     token: str = Depends(auth.oauth2_scheme),
                     db: Session = Depends(get_db)):
    try:
        data = CRUD_Auth.get_all_tenants_info(db)
        return Utils.create_response(status_code=200,
                                     success=True,
                                     data=data)
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )
