

from polling.base_polling import BasePolling
from schemas.primitive import PrimitiveStatus
import schemas.message as MessageSchemas
from aux.enums import ActionStatus
import aux.constants as Constants
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED
import copy
import logging
import asyncio
from typing import Union
from rabbitmq.adaptor import rabbit_handler
import json
import time

logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)

class MemPolling(BasePolling):
    def __init__(self) -> None:
        super().__init__()
        self.tasks = {}
    
        self.action_ending_states = [ActionStatus.COMPLETED.value,
                                     ActionStatus.FAILED.value]

    def is_job_already_running(self, vsiId):
        vsiId = str(vsiId)
        vsis_running = self.scheduler.get_jobs('default')
        return any([vsi.id == vsiId for vsi in vsis_running])

    def start_vsi_polling(self, vsiId):
        vsiId = str(vsiId)
        if self.is_job_already_running(vsiId):
            logging.info(f"Job for vsi {vsiId} already running."
                         + " No additional job will be created")
            return
        logging.info(f"Primitive Polling started for VSI {vsiId}")
        self.tasks[vsiId] = {}
        self.scheduler.add_job(
            self.poll_vsi,
            'interval', seconds=10, args=[vsiId], id=vsiId)
        self.scheduler.add_listener(
            self.my_listener,
            EVENT_JOB_ERROR | EVENT_JOB_MISSED)
    
    async def get_running_tasks(self, vsiId):
        await asyncio.sleep(0)
        vsiId = str(vsiId)
        if vsiId in self.tasks:
            return self.tasks[vsiId]
        return {}

    async def update_primitive_data(
    self,
    vsiId,
    data: Union[MessageSchemas.ActionNsData, MessageSchemas.ActionResponseData]):
        await asyncio.sleep(0)
        stored_data = PrimitiveStatus(
            isAlarm=True)
       
        if isinstance(data, MessageSchemas.ActionNsData):
            
            stored_data.domainId = data.domainId
            stored_data.actionId = data.actionId 

            self.tasks[vsiId][data.actionId] = stored_data
        else:
            logging.info(f"Updating primitive data {type(data)} {data.status}")
            self.tasks[vsiId][data.actionId].nfvoId = data.nfvoId
            self.tasks[vsiId][data.actionId].output = data.output
            self.tasks[vsiId][data.actionId].status = data.status
        return self.tasks


    async def poll_vsi(self, vsiId):
        primitives_running = await self.get_running_tasks(vsiId)
        logging.info(f"Polling.... {primitives_running}")

        await self.poll_vsi_primitive_status(vsiId, primitives_running)
    

    async def poll_vsi_primitive_status(self, vsiId: int, data):
        data_copy = copy.deepcopy(data)
        logging.info(f"ITEMS {data.items()}")
        for primitive_id, op_data in data.items():
            if op_data.status in self.action_ending_states:
                logging.info("Removing primitive Polling"
                             + "since it has ended its lifecycle")
                del data_copy[primitive_id]
                continue
            if op_data.nfvoId:
                data = MessageSchemas.FetchPrimitiveData(
                    domainId=op_data.domainId,
                    nfvoId=op_data.nfvoId,
                    actionId=primitive_id,
                    isAlarm=op_data.isAlarm
                )
                msg = MessageSchemas.Message(
                    vsiId=vsiId,
                    msgType=Constants.TOPIC_FETCH_ACTION_INFO,
                    data=data)
                logging.info(f"Sent message with type {msg.msgType}")
                await rabbit_handler.publish_queue(
                    Constants.QUEUE_DOMAIN,
                    json.dumps(msg.dict()))
                time.sleep(5)