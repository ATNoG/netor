# @Author: Daniel Gomes
# @Date:   2022-08-23 14:37:01
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-26 10:01:39
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
                                     data={"user_info": user_info})
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )
      


# @router.post(
#     "/users/register/",
#     tags=["auth"],
#     summary="Register user",
#     description="This endpoint allows the user to register using credentials.",
# )
# def register_new_user(new_user: AuthSchemas.UserRegister, token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
#     try:
#         login_username = auth.get_current_user(token)
#         roles = CRUD_Auth.get_user_roles(db, login_username)
#         # check if operation was ordered by an admin
#         if "ADMIN" not in roles:
#             raise NotEnoughPrivileges(login_username, 'register_new_user')
#         # create new user
#         db_user = CRUD_Auth.register_user(db, new_user.username, new_user.password, new_user.roles)
#         user_info = CRUD_Auth.get_user_info(db, db_user.username)
#     except Exception as e:
#         return Utils.create_response(status_code=401, success=False, errors=[e.message]) 
#     return Utils.create_response(status_code=200, success=True, data={"new_user": user_info})  



# @router.patch(
#     "/users/update-password/",
#     tags=["auth"],
#     summary="Update Password",
#     description="This endpoint allows the user to update his password."
# )
# def update_password(password_data: AuthSchemas.NewPassword, token: str = Depends(auth.oauth2_scheme) , db: Session = Depends(get_db)):
#     try:
#         username = auth.get_current_user(token)
#         db_user = CRUD_Auth.update_user_password(db, username, password_data.new_password)
#     except Exception as e:
#         return Utils.create_response(status_code=403, success=False, errors=[e.message]) 
#     return Utils.create_response(status_code=200, success=True, message="Password Updated With Success")  
