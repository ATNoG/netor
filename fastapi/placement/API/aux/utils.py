# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-03 00:38:05


from typing import List
from fastapi.responses import JSONResponse
from schemas.auth import Tenant
from sqlalchemy.orm import Session
import aux.constants as Constants
import schemas.auth as AuthSchemas
from fastapi.encoders import jsonable_encoder
import schemas.message as MessageSchemas
from idp.idp import idp
import json
# custom imports


def create_response(status_code=200, data=[], errors=[],
                    success=True, message=""):
    return JSONResponse(status_code=status_code,
                        content={"message": message, "success": success,
                                 "data": data, "errors": errors},
                        headers={"Access-Control-Allow-Origin": "*"})


def check_admin_role(data: AuthSchemas.Tenant):
    return Constants.IDP_ADMIN_USER in data.roles


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


def prepare_translation(
                        domainId: str,
                        sliceEnabled: bool,
                        nsdId: str = None,
                        nstId: str = None,
                        translation_set: List = []):
    obj = MessageSchemas.TranslationInfoData(
        domainId=domainId,
        sliceEnabled=sliceEnabled,
        nsdId=nsdId,
        nstId=nstId
    )
    if translation_set:
        translation_set.append(obj)
    else:
        translation_set = [obj]
    return translation_set


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
