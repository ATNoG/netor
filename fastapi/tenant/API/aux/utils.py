# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-01 16:56:17


from functools import wraps
from http.client import HTTPException
from fastapi.responses import JSONResponse
from exceptions.auth import NotEnoughPrivileges
from schemas.auth import Tenant
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
# custom imports
import aux.auth as auth
import sql_app.crud.auth as AuthCRUD

def create_response(status_code=200, data=[], errors=[],
                    success=True, message=""):
    return JSONResponse(status_code=status_code,
                        content={"message": message, "success": success,
                                 "data": data, "errors": errors},
                        headers={"Access-Control-Allow-Origin": "*"})


def rbac_enforcer(roles: list) -> None:
    def inner(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            token = kwargs.get('token')
            db = kwargs.get('db')
            try:
                username = auth.get_current_user(token)
                user_roles = AuthCRUD.get_user_roles(db, username)
                if not (set(roles) & set(user_roles)):
                    raise Exception
            except Exception as exception:
                return create_response(
                    status_code=400,
                    success=False,
                    errors=["Insufficient permissions to access this " +
                            "resource. This is resource is only available to" +
                            f" users with the roles: '{roles}', {exception}"]
                    )
            return await func(*args, **kwargs)
        return wrapper
    return inner

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


def check_permission_on_group(db: Session,
                                requester_username: str,
                                group_name: str):
    user_roles = AuthCRUD.get_user_roles(db, requester_username)
    if "ADMIN" not in user_roles:
        db_tenant = AuthCRUD.getTenantByUsername(db, requester_username)
        if db_tenant.group.name != group_name:
            raise NotEnoughPrivileges(requester_username)