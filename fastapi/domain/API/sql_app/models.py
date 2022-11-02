# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-01 12:00:50

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

# custom imports
from .database import Base


associationTable = Table(
                'DomainOwnedLayers',
                Base.metadata,
                Column('domainId', String, ForeignKey('Domain.domainId')),
                Column('domainLayerId', String, ForeignKey(
                    'DomainLayer.domainLayerId')))


class Domain(Base):
    __tablename__ = 'Domain'
    domainId = Column(String, primary_key=True)

    admin = Column(String)
    description = Column(String)
    auth = Column(Boolean)
    interfaceType = Column(String)
    port = Column(Integer, nullable=True)
    url = Column(String)
    status = Column(String)
    name = Column(String)
    owner = Column(String)
    ownedLayers = relationship(
                "DomainLayer",
                secondary=associationTable,
                back_populates="domains")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class DomainLayer(Base):
    __tablename__ = 'DomainLayer'
    domainLayerId = Column(String, primary_key=True)
    domainLayerType = Column(String)
    domains = relationship("Domain",
                           secondary=associationTable,
                           back_populates="ownedLayers")
    __mapper_args__ = {
        'polymorphic_identity': 'DomainLayer',
        'polymorphic_on': domainLayerType
    }

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class OsmDomainLayer(DomainLayer):
    __tablename__ = 'OsmDomainLayer'
    domainLayerId = Column(String,
                           ForeignKey('DomainLayer.domainLayerId'),
                           primary_key=True)
    username = Column(String)
    password = Column(String)
    project = Column(String)
    vimAccount = Column(String)
    ranEnabled = Column(Boolean, nullable=True, default=False)
    __mapper_args__ = {
        'polymorphic_identity': 'OSM_NSP',
    }

    def as_dict(self):
        layer = {c.name: getattr(self, c.name)
                 for c in self.__table__.columns}
        del layer['password']
        return layer
