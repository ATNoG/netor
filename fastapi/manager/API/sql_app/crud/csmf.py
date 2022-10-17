# @Author: Daniel Gomes
# @Date:   2022-09-26 17:24:14
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-10 12:00:19
from datetime import datetime
import json
import logging
from sqlalchemy.orm import Session
import aux.utils as Utils
from aux.enums import VSIStatus
# custom imports
from .. import models
import schemas.auth as AuthSchemas
import schemas.vertical as VerticalSchemas
import aux.constants as Constants
from sql_app.database import SessionLocal
import schemas.message as MessageSchemas
# Logger
logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)



def getCSMFByVSiId(db: Session, vsi_id: str):
    vs = db.query(models.CSMF)\
           .filter(models.CSMF.vsiId == vsi_id)\
           .first()
    return vs

def getAllCSMFs(db: Session):
    vs = db.query(models.CSMF).all()
    return vs
def createCSMF(db:Session, payload: MessageSchemas.Message):
    db_csmf = models.CSMF(
        vsiId=payload.vsiId,
        vsi_status=VSIStatus.CREATED,
        vsi_request=json.dumps(payload.dict())
    )
    db.add(db_csmf)
    db.commit()
    db.refresh(db_csmf)
    return db_csmf


def updateCSMFStatus(db: Session, vsiId, status: VSIStatus):
    db_obj = getCSMFByVSiId(db, vsiId)
    db_obj.status = status
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
