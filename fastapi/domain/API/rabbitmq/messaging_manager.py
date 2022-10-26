# @Author: Daniel Gomes
# @Date:   2022-08-16 16:19:06
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-12 17:52:38
import asyncio
import threading
from rabbitmq.adaptor import RabbitHandler
from aio_pika import IncomingMessage, Message
import json
import logging
import schemas.message as MessageSchemas
import aux.constants as Constants
from sql_app.database import SessionLocal
import sql_app.crud.domain as CRUDDomain
from aux.domain_action_handler import DomainActionHandler
import concurrent.futures

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

    def __init__(self):
        self.messaging = RabbitHandler()
        #self.loop = self._start_async()
    async def start(self):
        await self.messaging.start_pool()
        await self.messaging.create_exchange("vsLCM_Management")
        await self.messaging.create_queue("vsDomain")
        await self.messaging.consumeQueue("vsDomain", self.exchangeCallBack)
        await self.messaging.consumeExchange("vsLCM_Management", self.callback)

    async def exchangeCallBack(self, message: IncomingMessage):
        async with message.process():
            msg = message.body.decode()
            msg = json.loads(msg)
            payload = MessageSchemas.Message(**msg)
            
            logging.info(payload)
            handler = DomainActionHandler(payload, self.messaging)
            await handler.start()
            
    
            
    async def callback(self, message: IncomingMessage):
        async with message.process():
            msg = message.body.decode()
            msg = json.loads(msg)
            try:
                payload = MessageSchemas.Message(**msg)
            except Exception:
                logging.info(f"Could not read message {msg}")
                # if the message was not suposed to be received
                return
            if payload.msgType == Constants.TOPIC_CREATEVSI:
                try:
                    domainsIds = CRUDDomain.getDomainsIds()
                    payload.data = MessageSchemas.DomainInfoData(
                        domainIds=domainsIds)
                    payload.msgType = Constants.TOPIC_DOMAININFO
                    payload.error = False
                except Exception as e:
                    # Send error Message
                    payload.msgType = Constants.TOPIC_ERROR
                    payload.error = True
                    payload.message = f"Error when fetching domains ids: {e}"
                payload = payload.dict(exclude_none=True)

                logging.info("sent message:" + str(payload))
                await self.messaging.publish_exchange(Constants.EXCHANGE_MGMT,
                                                      json.dumps(payload))

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