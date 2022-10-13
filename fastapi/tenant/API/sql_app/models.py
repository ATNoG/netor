# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-01 10:14:55

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

# custom imports
from .database import Base


class Tenant_Role(Base):
    __tablename__ = "tenant_role"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, ForeignKey("Tenant.username"),
                  nullable=False, index=True)
    role = Column(Integer, ForeignKey("role.id"), nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, unique=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Group(Base):
    __tablename__ = 'Group'
    name = Column(String, primary_key=True)
    tenants = relationship("Tenant", back_populates="group")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Sla(Base):
    __tablename__ = 'Sla'
    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean)
    tenantUsername = Column(String, ForeignKey('Tenant.username'),
                      nullable=False)
    tenant = relationship("Tenant", back_populates="slas")
    constraints = relationship("SlaConstraint", back_populates="sla")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class SlaConstraint(Base):
    __tablename__ = 'SlaConstraint'
    id = Column(Integer, primary_key=True)
    storage = Column(Integer)
    memory = Column(Integer)
    vcpu = Column(Integer)
    scope = Column(Integer)
    location = Column(String)
    slaId = Column(Integer, ForeignKey('Sla.id'), nullable=False)
    sla = relationship("Sla", back_populates="constraints")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class VSD(Base):
    __tablename__ = 'VSD'
    id = Column(Integer, primary_key=True)
    tenantUsername = Column(String, ForeignKey('Tenant.username'),
                      primary_key=True)
    tenant = relationship("Tenant", back_populates="vsds")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class VSI(Base):
    __tablename__ = 'VSI'
    id = Column(String, primary_key=True)
    tenantUsername = Column(String, ForeignKey('Tenant.username'),
                      primary_key=True)
    tenant = relationship("Tenant", back_populates="vsis")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Tenant(Base):
    __tablename__ = 'Tenant'
    username = Column(String, primary_key=True, index=True)
    password = Column(String)
    groupName = Column(String, ForeignKey('Group.name'))
    group = relationship("Group", back_populates="tenants")
    vsds = relationship("VSD", back_populates="tenant")
    vsis = relationship("VSI", back_populates="tenant", cascade="all, delete-orphan")
    slas = relationship("Sla", back_populates="tenant")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}