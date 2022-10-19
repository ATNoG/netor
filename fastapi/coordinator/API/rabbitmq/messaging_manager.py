# @Author: Daniel Gomes
# @Date:   2022-08-16 16:19:06
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-19 22:07:55
import asyncio
import threading
from rabbitmq.adaptor import RabbitHandler
from aio_pika import IncomingMessage, Message
import json
import logging
import schemas.message as MessageSchemas
import aux.constants as Constants
from sql_app.database import SessionLocal
import sql_app.crud.vertical as CRUDVertical
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

logging.basicConfig(
    format="%(asctime)s %(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)



class MessageReceiver():

    def __init__(self, messaging=None):
        self.messaging = messaging
        if not messaging:
            self.messaging = RabbitHandler()

    async def start(self):
        await self.messaging.start_pool()
        await self.messaging.create_exchange(Constants.EXCHANGE_MGMT)
        await self.messaging.create_queue(Constants.QUEUE_COORDINATOR)
        await self.messaging.consumeQueue(Constants.QUEUE_COORDINATOR,
                                          self.callback)            
            
    async def callback(self, message: IncomingMessage):
        async with message.process():
            db_gen = get_db()
            db = next(db_gen)
            msg = message.body.decode()
            msg = json.loads(msg)
            try:
                payload = MessageSchemas.Message(**msg)
            except Exception:
                # if the message was not suposed to be received
                return
            logging.info(f"Received message in Coordinator: {payload}")
            if payload.msgType == Constants.TOPIC_VSI_STATUS:
                try:
                    CRUDVertical.changeVsiStatus(db, payload)
                    # no need to send message when success..for now
                except Exception as e:
                    # Send error Message
                    payload.msgType = Constants.TOPIC_ERROR
                    payload.error = True
                    payload.message = f"Error while updating vsi status: {e}"
                    payload = payload.dict(exclude_none=True)

                    logging.info("sent message:" + str(payload))
                    await self.messaging.publish_exchange(
                        Constants.EXCHANGE_MGMT,
                        json.dumps(payload))
            elif payload.msgType == Constants.TOPIC_ACTION_STATUS:
                    CRUDVertical.changeActionStatus(db, payload)
                
        
    def stop(self):
        try:
            self.messaging.stopConsuming()
        except Exception as e:
            logging.error("Pika exception: "+str(e))

    def run(self):
        try:
            logging.info('Started Consuming RabbitMQ Topics')
            
        except Exception as e:
            logging.info("Stop consuming now!")
            logging.error("Pika exception: "+str(e))