# @Author: Daniel Gomes
# @Date:   2022-09-06 16:14:44
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-26 16:48:16

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
                  userdata=Depends(Utils.rbacencforcer),
                  db: Session = Depends(get_db)):
    try:
        if not Utils.check_admin_role(userdata):
            raise NotEnoughPrivileges(userdata.username)
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
                userdata=Depends(Utils.rbacencforcer),
                db: Session = Depends(get_db)):
    try:

        db_vs = CRUDVertical.getVSById(db, vs_in.vsiId)
        if db_vs:
            raise VerticalAlreadyExists(vs_in.vsiId)
        
        # verify if VS Descriptor exists
        data = Utils.get_catalogue_vsd_info(userdata.token, vs_in.vsdId)
        if not data:
            raise VSDNotFound(vs_in.vsdId)

        # # verify if domain placements exists
        for domain in vs_in.domainPlacements:
            data = Utils.get_domain_info(userdata.token, domain.domainId)
            if not data:
                raise DomainNotFound(domain_id=domain.domainId)
        # Store in DB
        vs_out = CRUDVertical.createNewVS(db, userdata.username, vs_in)

        # dns_info = original_request["DNSInfo"]
        power_dns_client = Netor_DNS_SD(
            dns_ip=Constants.DNS_IP,
            api_port=Constants.DNS_API_PORT,
            vsi_id=vs_out.vsiId,
            api_key=Constants.DNS_API_KEY
        )
        power_dns_client.create_zone()
        vs_in = Utils.parse_dns_params_to_vnf(vs_in)
        # Send Message to the MessageBus
        msg = MessageSchemas.Message(
            vsiId=vs_in.vsiId,
            msgType=Constants.TOPIC_CREATEVSI,
            tenantId=userdata.username
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
                vsiId: str,
                userdata=Depends(Utils.rbacencforcer),
                db: Session = Depends(get_db)):
    
    try:
        db_vs = CRUDVertical.getVSById(db, vsiId, include_actions=True)
        if not db_vs:
            raise VerticalNotFound(vsiId)
        CRUDVertical.verify_vsi_ownership(db_vs, userdata)
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
async def executePrimitive(vsiId: str,
                     primitive_data: MessageSchemas.PrimitiveData,
                     userdata=Depends(Utils.rbacencforcer),
                     db: Session = Depends(get_db)):
    try:
        db_vs = CRUDVertical.getVSById(db, vsiId )
        if not db_vs:
            raise VerticalNotFound(vsiId)
        CRUDVertical.verify_vsi_ownership(db_vs, userdata)

        db_obj = CRUDVertical.createVSiAction(db, vsiId, primitive_data)

        message = MessageSchemas.Message(vsiId=vsiId,
         msgType=Constants.TOPIC_PRIMITIVE)
        message.data = primitive_data
        # await rabbit_handler.publish_exchange(
        #     Constants.EXCHANGE_MGMT,
        #     message=message)
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
def getVSiStatusHistory(vsiId: str,
                        userdata=Depends(Utils.rbacencforcer),
                        db: Session = Depends(get_db)):
    try:
        db_vs = CRUDVertical.getVSById(db, vsiId )
        if not db_vs:
            raise VerticalNotFound(vsiId)
        CRUDVertical.verify_vsi_ownership(db_vs, userdata)
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
async def deleteVSI(vsiId: str,
                force: bool=False,
                userdata=Depends(Utils.rbacencforcer),
                db: Session= Depends(get_db)):
    try:
        db_vs = CRUDVertical.getVSById(db, vsiId )
        if not db_vs:
            raise VerticalNotFound(vsiId)
        CRUDVertical.verify_vsi_ownership(db_vs, userdata)
        data = CRUDVertical.deleteVSI(db, vsiId)
        msg_data = MessageSchemas.DeleteVsiData(
            force=force
        )
        message = MessageSchemas.Message(vsiId=vsiId,
            msgType=Constants.TOPIC_PRIMITIVE,
            data=msg_data
        )
        await rabbit_handler.publish_exchange(
            Constants.EXCHANGE_MGMT,
            message
        )
        return Utils.create_response(
            data=data,
            message="Success Deleting Vertical",
        )
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )