# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-23 11:28:43


from http.client import HTTPException
from fastapi.responses import JSONResponse
from exceptions.domain import CouldNotAuthenticatetoNFVO
from schemas.auth import Tenant
import requests
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
# custom imports


def create_response(status_code=200, data=[], errors=[],
                    success=True, message=""):
    return JSONResponse(status_code=status_code,
                        content={"message": message, "success": success,
                                 "data": data, "errors": errors},
                        headers={"Access-Control-Allow-Origin": "*"})


def rbacencforcer():
    try:
        userdata = Tenant(username="User", role="Admin")
        return userdata
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Insufficient permissions to access this" +
                   " resource. This is resource is only available to")


def connect_to_nfvo(url, username, password, project_id):
    r = requests.post(
        url=f"{url}/osm/admin/v1/tokens",
        data={
            'username': username,
            'password': password,
            'project_id': project_id
        },
        timeout=5,
        verify=False
    )
    if r.status_code != 200:
        raise CouldNotAuthenticatetoNFVO()


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