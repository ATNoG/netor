# @Author: Daniel Gomes
# @Date:   2022-08-16 16:19:06
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-06 10:25:15

from contextlib import contextmanager
from redis.handler import RedisHandler
from rabbitmq.adaptor import RabbitHandler
from aio_pika import IncomingMessage
import json
import logging
import schemas.message as MessageSchemas
import aux.constants as Constants
import aux.utils as Utils
from csmf.csmf_handler import csmf_handler
from fastapi_events.dispatcher import dispatch
from sql_app.database import get_db


logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)


class MessageReceiver():

    def __init__(self, messaging=None, caching=None):
        self.messaging = messaging
        self.caching = caching
        if not messaging:
            self.messaging = RabbitHandler()
        if not caching:
            self.caching = RedisHandler()

    async def start(self):
        await self.messaging.start_pool()
        await self.messaging.create_exchange(Constants.EXCHANGE_MGMT)
        await self.messaging.consumeExchange(
            Constants.EXCHANGE_MGMT, self.callback)
            
    async def callback(self, message: IncomingMessage):
        async with message.process():
            msg = message.body.decode()
            msg = json.loads(msg)
            try:
                payload = MessageSchemas.Message(**msg)
            except Exception:
                logging.info(f"Message Not supported: {msg}")
                # if the message was not suposed to be received
                return
            logging.info(f"Received message in Manager: {payload}")
            res = MessageSchemas.Message(vsiId=payload.vsiId)
            if payload.msgType == Constants.TOPIC_CREATEVSI:
                with contextmanager(get_db)() as db:
                    a = await Utils.is_csmf_data_stored(
                        db,
                        self.caching,
                        Constants.TOPIC_CREATEVSI,
                        payload.vsiId
                        )
                    if a:
                        return
                # If its Neither in Cache or in Database then store data
                logging.info("NO Information found, starting CSMF")
                await csmf_handler.store_new_csmf(payload)
                # store tenant info, similarly to catalogue info

                data = MessageSchemas.StatusUpdateData(
                    status=Constants.CREATING_STATUS
                )
                res = Utils.prepare_message(
                    res,
                    data=data,
                    msg="Created Management Function, waiting to"\
                        + "receive all necessary information"
                )
            elif payload.msgType in Constants.INFO_TOPICS:
                dispatch(f'event-{payload.msgType}',
                         payload=payload,
                         middleware_id=Constants.EVENT_HANDLER_ID)
            else:
                dispatch(payload.msgType,
                         payload=payload,
                         middleware_id=Constants.EVENT_HANDLER_ID)
            # except Exception as e:
            #      logging.info(f"Error in Manager {e}")

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
