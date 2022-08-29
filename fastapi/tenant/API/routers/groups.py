# @Author: Daniel Gomes
# @Date:   2022-08-26 09:31:05
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-26 09:39:49
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


@router.get(
    "/group",
    tags=["group"],
    summary="Get All groups",
    description="This endpoint allows the groups in the system.",
)
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