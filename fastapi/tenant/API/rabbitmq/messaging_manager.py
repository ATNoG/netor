# @Author: Daniel Gomes
# @Date:   2022-08-16 16:19:06
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-12 17:56:28
from rabbitmq.adaptor import RabbitHandler
from aio_pika import IncomingMessage
import json
import logging
import aux.constants as Constants
from sql_app.database import SessionLocal
import schemas.message as MessageSchemas
import sql_app.crud.auth as CRUDAuth
import aux.utils as Utils
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
            try:
                payload = MessageSchemas.Message(**msg)
            except Exception:
                # if the message was not suposed to be received
                return
            db_gen = get_db()
            db = next(db_gen)
            try:
                if payload.msgType == Constants.TOPIC_CREATEVSI:

                    tenant_db = CRUDAuth.getTenantByUsername(
                        db, payload.tenantId)
                    tenant_roles = CRUDAuth.get_user_roles(
                        db, payload.tenantId)
                    tenant_out = MessageSchemas.TenantInfoData(
                            username=tenant_db.username,
                            group=tenant_db.group.name,
                            roles=tenant_roles
                        )
                    CRUDAuth.update_tenant_vs_data(db, tenant_db, payload.data)
                    payload.data = tenant_out
                    payload.msgType = Constants.TOPIC_TENANT_INFO

                elif payload.msgType == Constants.TOPIC_REMOVEVSI:
                    tenant_db = CRUDAuth.get_user_info(db, payload.tenantId)
                    CRUDAuth.update_tenant_vs_data(db, tenant_db, payload.data)
                else:
                    return
            except Exception as e:
                error_msg = f"Error performing {payload.msgType}" + \
                            f" in Tenant {payload}: {str(e)}"
                payload.msgType = Constants.TOPIC_ERROR
                payload.message = error_msg
            
        payload = payload.dict()
        logging.info("sent message:" + str(payload))
        await self.messaging.publish_exchange(
            Constants.EXCHANGE_MGMT,
            message=json.dumps(payload)
        )
        return

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
