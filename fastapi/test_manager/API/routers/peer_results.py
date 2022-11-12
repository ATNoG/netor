# @Author: Daniel Gomes
# @Date:   2022-11-12 08:35:03
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-12 10:50:05
from aux.file_manager import FileManager
from fastapi import APIRouter
import aux.utils as Utils
import logging
import inspect
import sys
import os
import schemas.timestamp as TimeStampSchemas
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


router = APIRouter()


@router.post(
    "/timestamp/{vsiId}",
    tags=["tests"],
    summary="Publish peer's instantiation time",
    description="Publish peer's instantiation time each instantiation step",
)
def publish_timestamp(
                      vsiId: int,
                      timestamp_data: TimeStampSchemas.TimestampData):
    
    file_manager = FileManager()
    file_manager.store_vsi_timestamp(vsi_id=vsiId, data=timestamp_data)
    return Utils.create_response(
        status_code=201,
        message="Sucess storing step timestamp"
    )
   
