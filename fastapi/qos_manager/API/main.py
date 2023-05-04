# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-12 10:26:10

from fastapi import FastAPI
import logging
import inspect
import sys
import os
from routers import alerts
# custom imports
import aux.startup as Startup
from rabbitmq.adaptor import rabbit_handler
import schemas.primitive as PrimitiveSchemas
import schemas.message as MessageSchemas
from redis.handler import redis_handler
import aux.constants as Constants
from rabbitmq.messaging_manager import MessageReceiver
import json
from qos.utils import lock
# import from parent directory
currentdir = os.path.dirname(os.path.abspath(
             inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


# Start Fast API
app = FastAPI(
    title="FastAPI Base Project",
    description="A base Project of FastAPI",
    version="0.0.1",
    contact={
        "name": "User",
        "email": "user@av.it.pt",
    },
    root_path="/qosmanager"
)
# app.add_middleware(
#     CORSMiddleware,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.include_router(alerts.router)
app.state.lock = lock

@app.on_event("startup")
async def startup_event():

    # Load Config
    ret, message = Startup.load_config()
    if not ret:
        logging.critical(message)
        return exit(1)
    await rabbit_handler.start_pool()
    redis_handler.start_connection()
    message_receiver = MessageReceiver(
        messaging=rabbit_handler)
    await message_receiver.start()

    # service_composition = PrimitiveSchemas.ServiceComposition(
    #     sliceEnabled=False,
    #     domainId="ITAV",
    #     nfvoId="e7deb086-3749-43e0-98c1-1e6cf9ebfe7a",
    #     status="Ok"
    # )
    # service_composition2 = PrimitiveSchemas.ServiceComposition(
    #     sliceEnabled=False,
    #     domainId="ITAV",
    #     nfvoId="8bfaa4bd-f2eb-4bd1-a71f-e3839ddb1ecd",
    #     status="Ok"
    # )
    # service_composition3 = PrimitiveSchemas.ServiceComposition(
    #     sliceEnabled=False,
    #     domainId="ITAV",
    #     nfvoId="e2426fbe-b7f0-4eae-a35c-ee9cbddb2087",
    #     status="Ok"
    # )
    # service_comp_dict = {
    #     "1-wireguard": service_composition,
    #     "2-wireguard": service_composition2,
    #     "3-wireguard": service_composition3
    # }
    # await redis_handler.store_vsi_service_composition(
    #     vsiId="1",
    #     data=service_comp_dict,
    #     parse_dict=True
    # )
    # msg = MessageSchemas.FetchNsInfoData(
    #     nsId=service_composition.nfvoId,
    #     domainId="ITAV"
    # )
    # await rabbit_handler.publish_queue(
    #                 Constants.QUEUE_DOMAIN,
    #                 json.dumps(msg.dict()))

# the qos manager may also have context about the verticals?s