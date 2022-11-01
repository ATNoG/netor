# @Author: Daniel Gomes
# @Date:   2022-08-16 14:21:19
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-01 23:22:58

import logging
from sqlalchemy.orm import Session
from exceptions.domain import DomainLayerTypeNotSupported
from sqlalchemy.orm import with_polymorphic
# custom imports
import aux.utils as Utils
from .. import models
import schemas.auth as AuthSchemas
import schemas.domain as DomainSchemas
import driver.driver_osm as driver_osm
import aux.constants as Constants
from sql_app.database import SessionLocal

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


def getAllDomains(db: Session, user: AuthSchemas.Tenant):
    domains = db.query(models.Domain).all()
    return [x.as_dict() for x in domains]


def getDomainById(db: Session, domainId: str):
    domain = db.query(models.Domain)\
               .filter(models.Domain.domainId == domainId)\
               .first()
    return domain


def getDomainsIds(db: Session = get_db()):
    db = next(db)
    domains = db.query(models.Domain).all()
    return [x.domainId for x in domains]


def getDomainLayerById(db: Session, layer: DomainSchemas.OwnedLayersCreate):
    entity = with_polymorphic(models.DomainLayer, "*")
    domain = db.query(entity)\
               .filter(entity.domainLayerId
                       == layer.domainLayerId)\
               .first()
    return domain


def getDomainDriver(self, domain_data: DomainSchemas.DomainCreate):
    driver = None
    for layer in domain_data.ownedLayers:
        if layer.domainLayerType == Constants.OSM_LAYER_TYPE:
            driver = driver_osm.OSMDriver(
                host=domain_data.url,
                username=layer.username,
                password=layer.password,
                project=layer.project,
            )
    return driver


def getDomainInfo(db: Session, domainId: int):
    domain = db.query(models.Domain).filter(
                      models.Domain.domainId == domainId)\
                                    .first()
    domainLayer = db.query(models.DomainLayer)\
                    .join(models.associationTable)\
                    .join(models.Domain)\
                    .filter(
                        models.associationTable.c.domainId
                        == models.Domain.domainId)\
                    .filter(
                        models.associationTable.c.domainLayerId
                        == models.DomainLayer.domainLayerId)\
                    .filter(models.DomainLayer.domainLayerType == 'OSM_NSP')\
                    .first()
    driver = None
    if domainLayer:
        osm_layer = db.query(models.OsmDomainLayer).filter(
            models.OsmDomainLayer.domainLayerId == domainLayer.domainLayerId
        ).first()
        driver = driver_osm.OSMDriver(
            host=domain.url,
            username=osm_layer.username,
            password=osm_layer.password,
            project=osm_layer.project,
        )
        domainLayer = osm_layer
    return domain, domainLayer, driver


def createDomain(db: Session, domain_data: DomainSchemas.DomainCreate):
    domain_obj = models.Domain(
            domainId=domain_data.domainId,
            admin=domain_data.admin,
            description=domain_data.description,
            auth=domain_data.auth,
            interfaceType=domain_data.interfaceType,
            url=domain_data.url,
            status=domain_data.status,
            name=domain_data.name,
            owner=domain_data.owner
    )

    for layer in domain_data.ownedLayers:
        if layer.domainLayerType == Constants.OSM_LAYER_TYPE:
            osmlayer_obj = models.OsmDomainLayer(
                domainLayerId=layer.domainLayerId,
                domainLayerType=layer.domainLayerType,
                username=layer.username,
                password=layer.password,
                project=layer.project,
                vimAccount=layer.vimAccount
            )
            domain_obj.ownedLayers.append(osmlayer_obj)
    db.add(domain_obj)
    db.commit()
    db.refresh(domain_obj)
    return domain_obj


def updateDomainLayer(db: Session,
                      domain_layer: DomainSchemas.OwnedLayersCreate):

    if domain_layer.domainLayerType not in Constants.DOMAIN_LAYER_TYPES:
        raise DomainLayerTypeNotSupported(domain_layer.domainLayerType)
    db_layer = getDomainLayerById(db, domain_layer)
    if db_layer:
        print(db_layer.__dict__)
        db_layer = Utils.update_db_object(
                db=db, db_obj=db_layer, obj_in=domain_layer, add_to_db=False)
    else:
        if domain_layer.domainLayerType == Constants.OSM_LAYER_TYPE:
            db_layer = models.OsmDomainLayer(
                domainLayerId=domain_layer.domainLayerId,
                domainLayerType=domain_layer.domainLayerType,
                username=domain_layer.username,
                password=domain_layer.password,
                project=domain_layer.project,
                vimAccount=domain_layer.vimAccount
            )
    return db_layer


def updateDomain(db: Session,
                 db_domain, domain_data: DomainSchemas.DomainUpdate):
    for layer in domain_data.ownedLayers:
        db_layer = updateDomainLayer(db, layer)
        db_domain.ownedLayers.append(db_layer)
        db.add(db_domain)
        db.commit()
        db.refresh(db_domain)
    domain_obj = Utils.update_db_object(db, db_domain, domain_data)
    domain_dict = domain_obj.as_dict()
    domain_dict['ownedLayers'] = [x.as_dict() for x in domain_obj.ownedLayers]
    return domain_dict


def deleteDomain(db: Session, db_domain):
    for layer in db_domain.ownedLayers:
        db.delete(layer)
    db.delete(db_domain)
    db.commit()
