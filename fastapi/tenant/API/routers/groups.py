# @Author: Daniel Gomes
# @Date:   2022-08-26 09:31:05
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-01 17:09:54
from datetime import timedelta
from fastapi import Depends
# generic imports
from fastapi import APIRouter
from sql_app.database import SessionLocal
from sqlalchemy.orm import Session
import logging
import inspect
import sys
import os
import sql_app.crud.auth as CRUD_Auth
from aux import auth
from exceptions.group import GroupAlreadyExists, GroupNotFound
# custom imports
import aux.utils as Utils
import schemas.group as GroupSchemas

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


@router.get(
    "/group",
    tags=["group"],
    summary="Get All groups",
    description="This endpoint allows getting all the groups in the system.",
)
@Utils.rbac_enforcer(['ADMIN'])
def getAllGroups(token: str = Depends(auth.oauth2_scheme),
                 db: Session = Depends(get_db)):
    try:
        groups = CRUD_Auth.get_all_groups(db)
        return Utils.create_response(
            data=groups,
            message="Success obtaining all groups"
        )
    except Exception as e:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(e)]
        )

@router.get(
    "/group/{group_name}",
    tags=["group"],
    summary="Get group by Name",
    description="This endpoint allows retrieving a group given its name",
)
@Utils.rbac_enforcer(['ADMIN','TENANT'])
def getGroupById(group_name: str,
                 token: str = Depends(auth.oauth2_scheme),
                 db: Session = Depends(get_db)):
    try:
        group = CRUD_Auth.get_group(db, name=group_name)
        if not group:
            raise GroupNotFound(group)
        username =  auth.get_current_user(token)
        Utils.check_permission_on_group(db,username,group_name)
        return Utils.create_response(
            data=group.as_dict(),
            message=f"Success obtaining Group with name {group_name}"
        )
    except Exception as e:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(e)]
        )

@router.post(
    "/group",
    tags=["group"],
    summary="Create a group",
    description="This endpoint allows the creation of a group.",
)
@Utils.rbac_enforcer(['ADMIN'])
def createGroup(group_in: GroupSchemas.GroupCreate,
                token: str = Depends(auth.oauth2_scheme),
                db: Session = Depends(get_db)):
    try:
        group = CRUD_Auth.get_group(db, group_in.name)
        if group:
            raise GroupAlreadyExists(group)
        group = CRUD_Auth.create_group(db, group_in.name)
        return Utils.create_response(
            data=group.as_dict(),
            message=f"Success creating Group with name {group_in.name}"
        )
    except Exception as e:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(e)]
        )