# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-03 00:37:54


import json
from fastapi.responses import JSONResponse
from schemas.auth import Tenant
from exceptions.auth import CouldNotConnectToDomain
import requests
from sqlalchemy.orm import Session
import aux.constants as Constants
import schemas.message as MessageSchemas
from fastapi.encoders import jsonable_encoder
from sql_app.crud import csmf as CsmfCRUD
from idp.idp import idp
# custom imports


def create_response(status_code=200, data=[], errors=[],
                    success=True, message=""):
    return JSONResponse(status_code=status_code,
                        content={"message": message, "success": success,
                                 "data": data, "errors": errors},
                        headers={"Access-Control-Allow-Origin": "*"})


def prepare_message(msg_base: MessageSchemas.Message, data=None,
                    error=False, msg="", tenantId=None,
                    msgType=None
                    ):
    msg_base.data = data
    msg_base.message = msg
    msg_base.tenantId = tenantId
    msg_base.error = error
    if msgType:
        msg_base.msgType = msgType
    return msg_base


def check_admin_role(user):
    return Constants.IDP_ADMIN_USER in user.roles


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


async def store_tenant_data(caching, vsiId: int, tenantId: str) -> Tenant:
    roles = idp.get_user_roles(user_id=tenantId)
    parsed_roles = [role.name for role in roles]
    username = idp.get_user(user_id=tenantId).username
    tenant = Tenant(id=tenantId, roles=parsed_roles, username=username)
    await caching.set_hash_key(
            vsiId,
            Constants.TOPIC_TENANTINFO,
            json.dumps(tenant.dict())
        )
    return tenant
