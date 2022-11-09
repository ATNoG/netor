# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-09 22:24:48

from fastapi import FastAPI
import logging
import inspect
import sys
import os
import time
# custom imports
from sql_app import models
from sql_app.database import SessionLocal, engine
from rabbitmq.adaptor import rabbit_handler
from rabbitmq.messaging_manager import MessageReceiver
import aux.startup as Startup
from routers.vertical import router as verticalrouter
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
    root_path="/lcm"
)
# app.add_middleware(
#     CORSMiddleware,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(verticalrouter)


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
    
    await rabbit_handler.start_pool()
   
    message_receiver = MessageReceiver(messaging=rabbit_handler)
    await message_receiver.start()
