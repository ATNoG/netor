# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-23 11:30:09

import json
from fastapi import FastAPI
import logging
import inspect
import sys
import os
import time
from rabbitmq.adaptor import RabbitHandler
import schemas.message as MessageSchemas
from routers import auth, domain
from rabbitmq.messaging_manager import MessageReceiver

# custom imports
from sql_app import models
from sql_app.database import SessionLocal, engine
import aux.startup as Startup
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
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.include_router(auth.router)
app.include_router(domain.router)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():

    # Load Config
    ret, message = Startup.load_config()
    if not ret:
        logging.critical(message)
        return exit(1)

    # Connect to Database
    MODELS_INITIALIZED = False
    for i in range(10):
        try:
            models.Base.metadata.create_all(bind=engine)
            MODELS_INITIALIZED = True
            break
        except Exception as e:
            print(f"entering..{e}")
            time.sleep(10)

    if not MODELS_INITIALIZED:
        exit(2)

    db = SessionLocal()

    # Store Initial Data in Database
    Startup.fill_database(db)
    message_receiver = MessageReceiver()
    await message_receiver.start()
    # msg_data = MessageSchemas.FecthNsiInfoData(
    #     domainId="ITAV", nsiId="d88a7919-8281-4369-bf25-afaea4766324")
    # msg = MessageSchemas.Message(
    #     vsiId=1,
    #     msgType="getNsiInfo",
    # )
    # msg.data = msg_data
    # a = json.dumps(msg.dict())
    # msg = MessageSchemas.Message(**json.loads(a))
    # await message_receiver.messaging.publish_queue('vsDomain', message=a)
    # await message_receiver.messaging.publish_queue('vsDomain', message=a)
