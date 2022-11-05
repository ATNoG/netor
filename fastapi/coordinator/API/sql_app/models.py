# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-05 18:05:07

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float,\
                       JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql.sqltypes import DateTime

# custom imports
from .database import Base


class VSIStatus(Base):
  __tablename__ = 'vsiStatus'
  status_id = Column(Integer, primary_key=True)
  vsiId = Column(Integer, ForeignKey('verticalServiceInstance.vsiId'))
  status=Column(String)
  statusMessage=Column(String)
  timestamp = Column(DateTime, default=datetime.utcnow)

  def as_dict(self):
    data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
    data['timestamp'] = str(data['timestamp'])
    return data



class VerticalServiceInstance(Base):
  __tablename__ = 'verticalServiceInstance'
  vsiId = Column(Integer, primary_key=True)
  description=Column(String)
  domainId=Column(String)
  statusMessage=Column(String)
  altitude=Column(Float)
  latitude=Column(Float)
  longitude=Column(Float)
  radioRange=Column(Float)
  mappedInstanceId=Column(String)
  name=Column(String)
  networkSliceId=Column(String)
  ranEndPointId=Column(String)
  status=Column(String)
  all_status= relationship('VSIStatus')
  tenantId=Column(String)
  vsdId=Column(String)
  nestedParentId = Column(Integer,
                          ForeignKey('verticalServiceInstance.vsiId'))
  nestedVsi=relationship("VerticalServiceInstance",
                         remote_side=[vsiId])
  nssis=relationship("NetworkSliceSubnetInstance",
                     back_populates="vertical_service_instance")
  vssis=relationship("VerticalSubserviceInstance",
                     back_populates="vertical_service_instance")
  domainPlacements=relationship("DomainPlacements",
                                back_populates="vertical_service_instance")
  additionalConf=relationship("ComponentConfigs",
                              back_populates="vertical_service_instance")

  def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class ComponentConfigs(Base):
  __tablename__ = 'componentConfigs'
  domainPlacementId = Column(Integer, primary_key=True)
  vertical_service_instance_id = Column(Integer, ForeignKey('verticalServiceInstance.vsiId'))
  vertical_service_instance = relationship("VerticalServiceInstance", back_populates="additionalConf")
  componentName=Column(String)
  conf=Column(JSON)

  def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class VSIAction(Base):
  __tablename__ = 'vsiAction'
  actstatus_id = Column(Integer, primary_key=True)
  primitiveName = Column(String)
  vsiId = Column(Integer, ForeignKey('verticalServiceInstance.vsiId'))
  status = Column(String, nullable=True)
  output = Column(String, nullable=True)
  def as_dict(self):
    data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
    return data

class DomainPlacements(Base):
  __tablename__ = 'domainPlacement'
  domainPlacementId = Column(Integer, primary_key=True)
  vertical_service_instance_id = Column(Integer, ForeignKey('verticalServiceInstance.vsiId'))
  vertical_service_instance = relationship("VerticalServiceInstance", back_populates="domainPlacements")
  componentName=Column(String)
  domainId=Column(String)

  def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class NetworkSliceSubnetInstance(Base):
  __tablename__ = 'networkSliceSubnetInstance'
  nssiId = Column(Integer, primary_key=True)
  domain_id=Column(String)
  ns_deployment_flavor_id=Column(String)
  ns_instantiation_level_id=Column(String)
  nsst_id=Column(String)
  status=Column(Integer)
  vertical_service_instance_id = Column(Integer, ForeignKey('verticalServiceInstance.vsiId'))
  vertical_service_instance = relationship("VerticalServiceInstance", back_populates="nssis") 
  vnfs = relationship("NetworkSliceSubnetInstanceVnfPlacement", back_populates="network_slice_subnet_instance")
  network_slice_instance_id = Column(Integer, ForeignKey('networkSliceInstance.nsiId'))
  network_slice_instance = relationship("NetworkSliceInstance", back_populates="subnets")

  def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class NetworkSliceSubnetInstanceVnfPlacement(Base):
  __tablename__ = 'networkSliceSubnetInstanceVnfPlacement'
  network_slice_subnet_instance_id = Column(Integer, ForeignKey('networkSliceSubnetInstance.nssiId'), primary_key=True)
  network_slice_subnet_instance = relationship("NetworkSliceSubnetInstance", back_populates="vnfs")
  vnf_placement_key=Column(Integer, primary_key=True)
  vnf_placement=Column(Integer)

  def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class VerticalSubserviceInstance(Base):
  __tablename__ = 'verticalSubserviceInstance'
  vssiId = Column(Integer, primary_key=True)
  blueprint_id=Column(String)
  descriptor_id=Column(String)
  domain_id=Column(String)
  instance_id=Column(String)
  vertical_service_status=Column(Integer)
  vertical_service_instance_id = Column(Integer, ForeignKey('verticalServiceInstance.vsiId'))
  vertical_service_instance = relationship("VerticalServiceInstance", back_populates="vssis")
  parameters=relationship("VerticalSubserviceInstanceParameters", back_populates="vertical_subservice_instance")

  def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class VerticalSubserviceInstanceParameters(Base):
  __tablename__ = 'verticalSubserviceInstanceParameters'
  vertical_subservice_instance_id = Column(Integer, ForeignKey('verticalSubserviceInstance.vssiId'), primary_key=True)
  vertical_subservice_instance = relationship("VerticalSubserviceInstance", back_populates="parameters")
  parameters_key=Column(Integer, primary_key=True)
  parameters=Column(String)

  def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class NetworkSliceInstance(Base):
  __tablename__ = 'networkSliceInstance'
  nsiId = Column(Integer, primary_key=True)
  name = Column(String)
  description = Column(String)
  nstId = Column(String)
  nsdId = Column(String)
  nsdVersion = Column(String)
  dfId = Column(String)
  instantiationLevelId = Column(String)
  oldInstantiationLevelId = Column(String)
  nfvNsId = Column(String)
  soManaged = Column(Boolean)
  tenantId = Column(String)
  status = Column(String)
  errorMessage = Column(String)
  nfvNsUrl = Column(String)
  subnets=relationship("NetworkSliceSubnetInstance",
                       back_populates="network_slice_instance")
  vnfs = relationship("NetworkSliceInstanceVnfPlacement",
                      back_populates="network_slice_instance")

  def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class NetworkSliceInstanceVnfPlacement(Base):
  __tablename__ = 'netwokSliceInstanceVnfPlacement'
  network_slice_instance_id = Column(Integer,
                                     ForeignKey('networkSliceInstance.nsiId'),
                                     primary_key=True)
  network_slice_instance = relationship("NetworkSliceInstance",
                                        back_populates="vnfs")
  vnf_placement_key=Column(Integer, primary_key=True)
  vnf_placement=Column(Integer)

  def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

