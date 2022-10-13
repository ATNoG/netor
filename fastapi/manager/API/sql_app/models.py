# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-28 11:22:55

from sqlalchemy import Boolean, Column, Enum, String, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql.sqltypes import DateTime
from aux.enums import VSIStatus
# custom imports
from .database import Base




class CSMF(Base):
  __tablename__ = 'csmf'
  vsiId = Column(String, primary_key=True)
  vsi_status = Column(Enum(VSIStatus), default=VSIStatus.CREATED)
  
  vsi_request = Column(String)

  def as_dict(self):
    data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
    return data
