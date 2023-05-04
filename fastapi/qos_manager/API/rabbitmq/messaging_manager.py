# @Author: Daniel Gomes
# @Date:   2022-08-16 16:19:06
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-29 22:42:29
from rabbitmq.adaptor import RabbitHandler
from aio_pika import IncomingMessage
import json
import logging
import schemas.message as MessageSchemas
import aux.constants as Constants
import aux.utils as Utils
from qos.manager import qos_manager

import aux.enums as Enums


logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)


class MessageReceiver():

    def __init__(self, messaging=None):
        self.messaging = messaging
        if not messaging:
            self.messaging = RabbitHandler()

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
                # if the message was not suposed to be received
                return
            logging.info(f"Received message in QoS Manager: {payload.msgType}")

            if payload.msgType == Constants.TOPIC_ACTION_RESPONSE:
                vsiId = str(payload.vsiId)
                if not payload.data.isAlarm:
                    return
                primitive_data = payload.data
                running_actions = await qos_manager.poller.get_running_tasks(
                    vsiId
                )
                logging.info(f"Running actions {running_actions}")
                stored_action_data = running_actions.get(str(primitive_data.actionId),
                                                 None)
                vsi_qos_obj = qos_manager.vsis[vsiId]
                if vsi_qos_obj.is_route_change_starting:
                    logging.info("Keeping track of a new Route change action..")
                    if stored_action_data:
                        stored_action_data.nfvoId = primitive_data.nfvoId
                        stored_action_data.status = primitive_data.status
                        stored_action_data.output = primitive_data.output
                    logging.info(f"ACTIOND_ID {primitive_data.actionId}" )
                    running_actions[primitive_data.actionId] = stored_action_data
                    await qos_manager.poller.update_primitive_data(
                        vsiId=vsiId,
                        data=stored_action_data)
                    # if the action has been completed then process the logic
                    if primitive_data.status == Enums.ActionStatus.COMPLETED.value:
                        msg = await qos_manager.apply_new_route(
                            vsiId,
                            payload.data
                        )
                        await self.messaging.publish_queue(
                            queue=Constants.QUEUE_DOMAIN,
                            message=json.dumps(msg.dict())
                        )
                    
                #route_manager.poller.update_primitive_data()
                

            
                
                
                
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