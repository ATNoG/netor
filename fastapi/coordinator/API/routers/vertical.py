# @Author: Daniel Gomes
# @Date:   2022-09-06 16:14:44
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-03 17:55:43

import json
from fastapi import Depends
# generic imports
from fastapi import APIRouter
from dns_sd.power_dns_wrapper import Netor_DNS_SD
from exceptions.auth import NotEnoughPrivileges
from exceptions.domain import DomainNotFound
from exceptions.catalogue import VSDNotFound
from sql_app.database import SessionLocal
from sqlalchemy.orm import Session
import logging
import inspect
import sys
import os
import sql_app.crud.vertical as CRUDVertical
import aux.utils as Utils
import aux.constants as Constants
import schemas.vertical as VerticalSchemas
import schemas.message as MessageSchemas
from exceptions.vertical import VerticalAlreadyExists, VerticalNotFound
from rabbitmq.adaptor import rabbit_handler
from idp.idp import idp
import aux.auth as auth
# import from parent directory
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(
                             inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# custom imports

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
    "/vs",
    tags=["vs"],
    summary="Return all the Vertical Services in the system",
    description="Return all the Vertical Services in the system",
)
def getAllVerticals(
                  user=Depends(idp.get_current_user(
                    required_roles=[Constants.IDP_ADMIN_USER])),
                  db: Session = Depends(get_db)):
    try:
        if not Utils.check_admin_role(user):
            raise NotEnoughPrivileges(user.preferred_username)
        vss = CRUDVertical.getAllVSs(db)
        return Utils.create_response(
            data=vss,
            message="Success obtaining All Verticals",
        )
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )


@router.post(
    "/vs",
    tags=["vs"],
    summary="Creates a new Vertical",
    description="Return all the Vertical Services in the system",
)
async def createnewVS(
                vs_in: VerticalSchemas.VSICreate,
                token: auth.OAuth2PasswordBearer = Depends(
                    auth.oauth2_scheme),
                user=Depends(idp.get_current_user(
                    required_roles=[Constants.IDP_ADMIN_USER])),
                db: Session = Depends(get_db)):
    try:
        #
        # verify if VS Descriptor exists
        data = Utils.get_catalogue_vsd_info(token, vs_in.vsdId)
        # if not data:
        #     raise VSDNotFound(vs_in.vsdId)
        # # # verify if domain placements exists
        for domain in vs_in.domainPlacements:
            data = Utils.get_domain_info(token, domain.domainId)
            if not data:
                raise DomainNotFound(domain_id=domain.domainId)
        # Store in DB
        vs_out = CRUDVertical.createNewVS(db, user.sub, vs_in)
        # create zone
        power_dns_client = Netor_DNS_SD(
            dns_ip=Constants.DNS_IP,
            api_port=Constants.DNS_API_PORT,
            vsi_id=vs_out.vsiId,
            api_key=Constants.DNS_API_KEY
        )
        power_dns_client.create_zone()
        # Now that we have a vertical Id we may customize the component names
        # to be easier to parse and inject the vertical Id on component's 
        # configuration
        # TODO: Find a better way to do this
        for i in range(len(vs_in.domainPlacements)):
            domain_placement = vs_in.domainPlacements[i]
            config = vs_in.additionalConf[i]
            new_name = f"{vs_out.vsiId}_{domain_placement.componentName}"
            CRUDVertical.updateComponentsNames(
                db,
                vsiId=vs_out.vsiId,
                previous_name=domain_placement.componentName,
                new_name=new_name)
            domain_placement.componentName = new_name
            config.componentName = new_name

        vs_in = Utils.parse_dns_params_to_vnf(vs_out.vsiId, vs_in)
        # Send Message to the MessageBus
        msg = MessageSchemas.Message(
            vsiId=vs_out.vsiId,
            msgType=Constants.TOPIC_CREATEVSI,
            tenantId=user.sub
        )

        data = MessageSchemas.CreateVsiData(**vs_in.dict())
        msg.data = data
        await rabbit_handler.publish_exchange(
            Constants.EXCHANGE_MGMT,
            json.dumps(msg.dict())
        )

        return Utils.create_response(
            status_code=201,
            data=vs_out.as_dict(),
            message="Success creating a new VS",
        )
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )


@router.get(
    "/vs/{vsiId}",
    tags=["vs"],
    summary="Return the Vertical Service requested",
    description="Returns the Vertical Service requested",
)
async def getVsiById(
                vsiId: int,
                user=Depends(idp.get_current_user(
                    required_roles=[Constants.IDP_ADMIN_USER])),
                db: Session = Depends(get_db)):
    try:
        db_vs = CRUDVertical.getVSById(db, vsiId, include_actions=True)
        if not db_vs:
            raise VerticalNotFound(vsiId)
        CRUDVertical.verify_vsi_ownership(db_vs, user)
        return Utils.create_response(
            data=db_vs,
            message="Success Getting a new VS",
        )
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )


@router.post(
    "/vs/{vsiId}/primitive",
    tags=["vs"],
    summary="Executes a primitive over an existent Vertical Slice",
    description="Executes a primitive over an existent Vertical Slice"
)
async def executePrimitive(
                    vsiId: int,
                    primitive_data: MessageSchemas.PrimitiveData,
                    user=Depends(idp.get_current_user(
                        required_roles=[Constants.IDP_ADMIN_USER])),
                    db: Session = Depends(get_db)):
    try:
        db_vs = CRUDVertical.getVSById(db, vsiId)
        if not db_vs:
            raise VerticalNotFound(vsiId)
        CRUDVertical.verify_vsi_ownership(db_vs, user)

        db_obj = CRUDVertical.createVSiAction(db, vsiId, primitive_data)

        message = MessageSchemas.Message(vsiId=vsiId,
                                         msgType=Constants.TOPIC_PRIMITIVE)
        message.data = primitive_data
        await rabbit_handler.publish_exchange(
            Constants.EXCHANGE_MGMT,
            message=json.dumps(message.dict()))
        return Utils.create_response(
            message="Primitive as been executed",
            data=db_obj)
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )


@router.get(
    "/vs/{vsiId}/status",
    tags=["vs"],
    summary="Returns All Status that a Vertical Slice has been through",
    description="Returns All Status that a Vertical Slice has been through",
)
def getVSiStatusHistory(vsiId: int,
                        user=Depends(idp.get_current_user(
                            required_roles=[Constants.IDP_ADMIN_USER])),
                        db: Session = Depends(get_db)):
    try:
        db_vs = CRUDVertical.getVSById(db, vsiId)
        if not db_vs:
            raise VerticalNotFound(vsiId)
        CRUDVertical.verify_vsi_ownership(db_vs, user)
        data = CRUDVertical.getAllVSIStatus(db, vsiId)
        return Utils.create_response(
            data=data,
            message="Success Getting all VSi Status History",
        )
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )


@router.delete(
    "/vs/{vsiId}",
    tags=["vs"],
    summary="Deletes the Vertical Service requested",
    description="Deletes the Vertical Service requested",
)
async def deleteVSI(vsiId: int,
                    user=Depends(idp.get_current_user(
                            required_roles=[Constants.IDP_ADMIN_USER])),
                    force: bool = False,
                    db: Session = Depends(get_db)):
    try:
        db_vs = CRUDVertical.getVSById(db, vsiId)
        if not db_vs:
            raise VerticalNotFound(vsiId)
        CRUDVertical.verify_vsi_ownership(db_vs, user)
        data = CRUDVertical.deleteVSI(db, vsiId)
        msg_data = MessageSchemas.DeleteVsiData(
            force=force
        )
        message = MessageSchemas.Message(
            vsiId=vsiId,
            msgType=Constants.TOPIC_REMOVEVSI,
            data=msg_data
        )
        await rabbit_handler.publish_exchange(
            Constants.EXCHANGE_MGMT,
            json.dumps(message.dict())
        )
        return Utils.create_response(
            data=data.as_dict(),
            message="Success Deleting Vertical",
        )
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )
