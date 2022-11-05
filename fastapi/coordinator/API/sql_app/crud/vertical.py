# @Author: Daniel Gomes
# @Date:   2022-09-06 16:52:10
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-05 18:04:37
from datetime import datetime
import logging
from sqlalchemy.orm import Session
import aux.utils as Utils
from exceptions.auth import NotEnoughPrivileges
from .. import models
from exceptions.vertical import InvalidComponentName
import schemas.vertical as VerticalSchemas
import aux.constants as Constants
from sql_app.database import SessionLocal
import schemas.message as MessageSchemas
from fastapi_keycloak import OIDCUser
# Logger
logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_vsi_ownership(
                         vsi_db: models.VerticalServiceInstance,
                         auth_data: OIDCUser):
    if not Utils.check_admin_role(auth_data):
        if vsi_db.tenantId != auth_data.sub:
            raise NotEnoughPrivileges()
    return True


def getAllVSs(db: Session):
    vss = db.query(models.VerticalServiceInstance)\
                .all()

    return [x.as_dict() for x in vss]


def getVSActionsByVsiId(db: Session, vsi_id: int):
    vs_actions = db.query(models.VSIAction)\
                   .filter(models.VSIAction.vsiId == vsi_id).all()
    return [action.as_dict() for action in vs_actions]


def getVSById(db: Session, vsi_id: int, include_actions=False):
    vs = db.query(models.VerticalServiceInstance)\
           .filter(models.VerticalServiceInstance.vsiId == vsi_id)\
           .first()
    if include_actions:
        vs = vs.as_dict()
        actions = getVSActionsByVsiId(db, vsi_id)
        vs['actions'] = actions
    return vs


def createVSiAction(db: Session, vsiId,
                    data: MessageSchemas.PrimitiveData):
    action_in = models.VSIAction(
        vsiId=vsiId,
        primitiveName=data.primitiveName
    )
    db.add(action_in)
    db.commit()
    db.refresh(action_in)
    return action_in.as_dict()


def updateComponentsNames(db: Session, vsiId: int,
                          previous_name: str, new_name: str):
    db.query(models.DomainPlacements)\
      .filter(models.DomainPlacements.vertical_service_instance_id == vsiId)\
      .filter(models.DomainPlacements.componentName == previous_name)\
      .update({models.DomainPlacements.componentName: new_name})
 
    db.query(models.ComponentConfigs)\
      .filter(models.ComponentConfigs.vertical_service_instance_id == vsiId)\
      .filter(models.ComponentConfigs.componentName == previous_name)\
      .update({models.ComponentConfigs.componentName: new_name})
    db.commit()


def createNewVS(db: Session,
                tenantId: str,
                vs_in: VerticalSchemas.VSICreate):

    vs_obj = models.VerticalServiceInstance(
       name=vs_in.name,
       description=vs_in.description,
       vsdId=vs_in.vsdId,
    )
    # verify component_Names:
    component_names = [x.componentName for x in vs_in.domainPlacements]
    conf_component_names = [x.componentName for x in vs_in.additionalConf]
    if set(component_names) != set(conf_component_names):
        raise InvalidComponentName()
    for domain in vs_in.domainPlacements:
        domain_obj = models.DomainPlacements(
            componentName=domain.componentName,
            domainId=domain.domainId
        )
        vs_obj.domainPlacements.append(domain_obj)
    for conf in vs_in.additionalConf:            
        vs_obj.additionalConf.append(models.ComponentConfigs(
            componentName=conf.componentName,
            conf=conf.conf
        ))

    vs_obj.tenantId = tenantId
    # Update Current Status
    vs_obj.status = Constants.CREATING_STATUS
    vs_obj.statusMessage = "Creating Vertical Service Instance"

    # Update list of all Status that the VSI has been through
    status_obj = models.VSIStatus(
        status=Constants.CREATING_STATUS,
        statusMessage="Creating Vertical Service Instance",
        timestamp=datetime.utcnow()
    )
    vs_obj.all_status = [status_obj]
    # Update Component Name to consider vsiId 
    db.add(vs_obj)
    db.commit()
    db.refresh(vs_obj)
    return vs_obj


def changeVsiStatus(db: Session, payload: MessageSchemas.Message):
    vsi = getVSById(db, payload.vsiId)
    if vsi and payload.data.status:
        if Constants.FAILING_STATUS not in vsi.all_status:
            logging.info("Updating Status of VSI...")
            vsi.status = payload.data.status
            vsi.statusMessage = payload.message
            status_db = models.VSIStatus(
                status=payload.data.status,
                statusMessage=payload.message,
                timestamp=datetime.utcnow()
            )
            vsi.all_status.append(status_db)
            logging.info(f"Status of VSI {payload.vsiId} updated")
            db.add(vsi)
            db.commit()
            db.refresh(vsi)
        if Constants.TERMINATED_STATUS in payload.data.status:
            db.delete(vsi)
            db.commit()


def changeActionStatus(db: Session, payload: MessageSchemas.Message):
    action = db.query(models.VSIAction)\
               .filter(models.VSIAction.actstatus_id == payload.data.actionId)\
               .first()
    if action:
        logging.info("Changing Action Status...")
        Utils.update_db_object(db, action, payload.data.dict())


def getAllVSIStatus(db: Session, vsiId):
    status = db.query(models.VSIStatus)\
            .filter(models.VSIStatus.vsiId == vsiId).all()
    return [stat.as_dict() for stat in status]


def deleteVSI(db: Session, vsiId: int):
    vs = getVSById(db, vsi_id=vsiId)
    db.delete(vs)
    db.commit()
    return vs
