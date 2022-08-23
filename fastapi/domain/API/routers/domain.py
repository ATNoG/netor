# @Author: Daniel Gomes
# @Date:   2022-08-16 11:57:43
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-23 11:31:57

from fastapi import Depends
# generic imports
from fastapi import APIRouter
from sql_app.database import SessionLocal
from sqlalchemy.orm import Session
import logging
import inspect
import sys
import os
import sql_app.crud.domain as CRUDDomain
import schemas.domain as DomainSchemas
import aux.utils as Utils
from exceptions.domain import DomainAlreadyExists
import aux.constants as Constants
from exceptions.domain import DomainLayerTypeNotSupported,\
     DomainLayerAlreadyExists, DomainNotFound

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
    "/domain/",
    tags=["domain"],
    summary="Return all the Domains in the system",
    description="Return all the Domains in the system",
)
def getAllDomains(
                  userdata=Depends(Utils.rbacencforcer),
                  db: Session = Depends(get_db)):
    domains = CRUDDomain.getAllDomains(db, userdata)
    return Utils.create_response(
        data=domains,
        message="Success obtaining Domains"
    )


@router.get(
    "/domain/{domainId}",
    tags=["domain"],
    summary="Return a Domain Requested",
    description="Given a Domain's Id returns the domain requested",
)
def getDomainById(
                  domainId: int,
                  userdata=Depends(Utils.rbacencforcer),
                  db: Session = Depends(get_db)):
    try:
        domain = CRUDDomain.getDomainById(db, domainId)
        if not domain:
            raise DomainNotFound(domain_id=domainId)
        return Utils.create_response(
            data=domain,
            message="Success obtaining Domain"
        )
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )


@router.post(
    "/domain",
    tags=['domain'],
    summary="Creates a new Domain"
)
def createNewDomain(
                    domain_data: DomainSchemas.DomainCreate,
                    user_data=Depends(Utils.rbacencforcer),
                    db: Session = Depends(get_db)):
    try:
        # Check if there's already a Domain with this Id
        domain_obj = CRUDDomain.getDomainById(db, domain_data.domainId)
        if domain_obj:
            raise DomainAlreadyExists(domain_id=domain_data.domainId)
        # Check if there's a domain layer with this id
        for layer in domain_data.ownedLayers:
            if layer.domainLayerType not in Constants.DOMAIN_LAYER_TYPES:
                raise DomainLayerTypeNotSupported(layer.domainLayerType)

        layer_obj = CRUDDomain.getDomainLayerById(
            db=db,
            layer=domain_data.ownedLayers[0]
        )
        if layer_obj:
            raise DomainLayerAlreadyExists(
                layer_obj.domainLayerId
            )
        driver = CRUDDomain.getDomainDriver(db, domain_data)
        # try to authenticate to the NFVO
        driver.authenticate()
        domain_data = CRUDDomain.createDomain(db, domain_data)
        return Utils.create_response(
            message="Success Creating new Domain",
            data=domain_data.as_dict()
        )
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )


@router.patch(
    "/domain/{domainId}",
    tags=["domain"],
    summary="Update the Information of a Domain",
    description="Given a Domain's Id updates its data",
)
def updateDomain(
                  domainId: str,
                  domain_data: DomainSchemas.DomainUpdate,
                  userdata=Depends(Utils.rbacencforcer),
                  db: Session = Depends(get_db)):
    try:
        domain = CRUDDomain.getDomainById(db, domainId)
        if not domain:
            raise DomainNotFound(domain_id=domainId)
        print(domain.ownedLayers)
        domain = CRUDDomain.updateDomain(db, domain, domain_data)
        driver = CRUDDomain.getDomainDriver(db, domain_data)
        # try to authenticate to the NFVO
        driver.authenticate()
        return Utils.create_response(
            data=domain,
            message="Success updating Domain"
        )
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )


@router.delete(
    "/domain/{domainId}",
    tags=["domain"],
    summary="Delete the Domain Requested",
    description="Given a Domain's Id deletes the domain requested",
)
def deleteDomain(
                  domainId: str,
                  userdata=Depends(Utils.rbacencforcer),
                  db: Session = Depends(get_db)):
    try:
        domain = CRUDDomain.getDomainById(db, domainId)
        if not domain:
            raise DomainNotFound(domain_id=domainId)
        CRUDDomain.deleteDomain(db, domain)
        return Utils.create_response(
            data=domain.as_dict(),
            message="Success Deleting Domain"
        )
    except Exception as exception:
        return Utils.create_response(
            status_code=400,
            success=False,
            errors=[str(exception)]
        )
