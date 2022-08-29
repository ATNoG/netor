# @Author: Daniel Gomes
# @Date:   2022-08-16 16:19:06
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-23 14:45:52
from rabbitmq.adaptor import RabbitHandler
from aio_pika import IncomingMessage
import json
import logging
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

    def __init__(self):
        self.messaging = RabbitHandler()

    async def start(self):
        await self.messaging.start_pool()
        await self.messaging.create_exchange(Constants.EXCHANGE_MGMT)
        await self.messaging.consumeExchange(Constants.EXCHANGE_MGMT,
                                             self.callback)

    async def callback(self, message: IncomingMessage):
        async with message.process():
            msg = message.body.decode()
            msg = json.loads(msg)
            # payload = MessageSchemas.Message(**msg)
            logging.info("here")

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
