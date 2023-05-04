# @Author: Daniel Gomes
# @Date:   2022-11-12 08:35:03
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-12 10:50:05
from fastapi import APIRouter, Request
import aux.utils as Utils
import logging
import inspect
import sys
import os
import schemas.alarms as AlarmSchemas
from qos.manager import qos_manager
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
    "/alerts",
    tags=["alerts"],
    summary="Publish peer's link alarm",
    description="Publish peer's link alarm due to a network bottleneck",
)
async def publish_alarm(
                  alarm: AlarmSchemas.LinkAlarmData,
                  request: Request):
    _app = request.app
    await qos_manager.add_vsi(
        alarm=alarm,
        app=_app
    )
    return Utils.create_response(
        status_code=201,
        message="Sucess storing step timestamp"
    )

@router.get("/hello")
async def hello_world():
    return {"message": "Hello World"}