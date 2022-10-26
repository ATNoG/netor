# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-01 08:44:12


import json
from typing import List
from fastapi.responses import JSONResponse
from fastapi import Depends, HTTPException
from exceptions.auth import CouldNotConnectToTenant, CouldNotConnectToDomain
from schemas.auth import Tenant
import requests
import aux.auth as auth
from sqlalchemy.orm import Session
import aux.constants as Constants
import schemas.auth as AuthSchemas
import schemas.message as MessageSchemas
from fastapi.encoders import jsonable_encoder
from sql_app.crud import csmf as CsmfCRUD
# custom imports


def create_response(status_code=200, data=[], errors=[],
                    success=True, message=""):
    return JSONResponse(status_code=status_code,
                        content={"message": message, "success": success,
                                 "data": data, "errors": errors},
                        headers={"Access-Control-Allow-Origin": "*"})


def prepare_message(msg_base: MessageSchemas.Message, data=None,
                    error=False, msg="", tenantId=None):
    msg_base.data = data
    msg_base.message = msg
    msg_base.tenantId = tenantId
    msg_base.error = error
    return msg_base

def rbacencforcer(token: str = Depends(auth.oauth2_scheme)):
    try:
        data = get_tenant_info(token)['data']['user_info']
        userdata = Tenant(**data)
        userdata.token = token
        return userdata
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail="Insufficient permissions to access this" +
                   " resource. This is resource is only available to")


def check_admin_role(data: AuthSchemas.Tenant):
    return "ADMIN" in data.roles



def get_tenant_info(token):
    url = f"http://{Constants.TENANT_HOST}:{Constants.TENANT_PORT}"\
          + "/oauth/validate"
    try:
        r = requests.get(
            url=url,
            headers={'Authorization': f'Bearer {token}'},
            timeout=5,
            verify=False
        )
        if r.status_code != 200:
            raise CouldNotConnectToTenant()
        data = r.json()
        
        return data
    except Exception:
        raise CouldNotConnectToTenant()

def get_domain_info(token, domain_id):
    url = f"http://{Constants.DOMAIN_HOST}:{Constants.DOMAIN_PORT}"\
          + f"/domain/{domain_id}"
    try:
        r = requests.get(
            url=url,
            headers={'Authorization': f'Bearer {token}'},
            timeout=5,
            verify=False
        )
        data = r.json()
        return data['data']
    except Exception:
        raise CouldNotConnectToDomain()


def update_db_object(db: Session, db_obj: object, obj_in: dict,
                     add_to_db: bool = True):
    obj_data = jsonable_encoder(db_obj)
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    if add_to_db:
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    return db_obj


async def is_csmf_data_stored(db: Session, caching, mainkey, key):
    data = await caching.get_hash_value(mainkey, key)
    if data:
        return data.decode()
    data = CsmfCRUD.getCSMFByVSiId(db, key)
    return data

async def verify_resource_operate_status(status: str,
                                         nsidata=None, nsdata=None):
    if (not nsidata and nsdata) or (nsidata and nsdata):
        return False
    elif nsidata:
        json_nsiInfo = json.loads(nsidata.nsiInfo)
        return json_nsiInfo['operational-status'] == status
    json_nsInfo = json.loads(nsidata.nsInfo)
    return json_nsInfo['operational-status'] == status
