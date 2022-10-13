# @Author: Daniel Gomes
# @Date:   2022-08-16 16:19:06
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-12 17:56:15
import asyncio
import threading
from arbitrator.arbitrator import Arbitrator
from redis.handler import RedisHandler
from rabbitmq.adaptor import RabbitHandler
from aio_pika import IncomingMessage
import json
import logging
import schemas.message as MessageSchemas
import aux.constants as Constants
from sql_app.database import SessionLocal

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)



class MessageReceiver():

    def __init__(self, messaging=None, caching= None):
        self.messaging = messaging
        self.caching = caching
        if not messaging:
            self.messaging = RabbitHandler()
        if not caching:
            self.caching = RedisHandler()
        self.arbitrator = Arbitrator(self.caching)

    async def start(self):
        await self.messaging.start_pool()
        await self.messaging.create_exchange(Constants.EXCHANGE_MGMT)
        await self.messaging.consumeExchange(
            Constants.EXCHANGE_MGMT, self.callback)
            
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
            logging.info(f"Received message in Placement: {payload}")

            if payload.msgType == Constants.TOPIC_CREATEVSI:
                await self.caching.store_vsi_initial_data(payload.vsiId)

            if payload.msgType == Constants.TOPIC_REMOVEVSI:
                await self.caching.tear_down_vsi_data(payload.vsiId)

            elif payload.msgType in Constants.INFO_TOPICS:
                res = await self.arbitrator.processAction(payload)
                if res:
                    await self.messaging.publish_exchange(
                        Constants.EXCHANGE_MGMT,
                        json.dumps(res.dict())
                    )
                
                
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