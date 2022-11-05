# @Author: Daniel Gomes
# @Date:   2022-09-26 21:53:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-05 21:18:58
import copy
import json
from typing import Dict
from aux.enums import ActionStatus
from redis.handler import redis_handler
from rabbitmq.adaptor import rabbit_handler
import schemas.message as MessageSchemas
import schemas.vertical as VerticalSchemas
import aux.constants as Constants
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED
import logging
from sql_app.database import SessionLocal
import sql_app.crud.csmf as CSMFCrud

logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Polling:
    def __init__(self) -> None:
        self.component = None
        self.running = True
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        self.action_ending_states = [ActionStatus.COMPLETED.value,
                                     ActionStatus.FAILED.value]

    def start_all_jobs(self):
        db_gen = get_db()
        db = next(db_gen)
        all_csmfs = CSMFCrud.getAllCSMFs(db)
        for csmf in all_csmfs:
            self.start_vsi_polling_csmf(csmf.vsiId)

    def is_job_already_running(self, vsiId):
        vsiId = str(vsiId)
        vsis_running = self.scheduler.get_jobs('default')
        return any([vsi.id == vsiId for vsi in vsis_running])

    def start_vsi_polling_csmf(self, vsiId):
        vsiId = str(vsiId)
        if self.is_job_already_running(vsiId):
            logging.info(f"Job for vsi {vsiId} already running."
                         + " No additional job will be created")
            return
        self.scheduler.add_job(
            self.pollVsiLCM,
            'interval', seconds=30, args=[vsiId], id=vsiId)
        logging.info(f"CSMF Polling started for VSI {vsiId}")
        self.scheduler.add_listener(
            self.my_listener,
            EVENT_JOB_ERROR | EVENT_JOB_MISSED)
    
    def stop_vsi_polling_csmf(self, vsiId):
        vsiId = str(vsiId)
        if not self.is_job_already_running(vsiId):
            logging.info(f"Job for vsi {vsiId} already running."
                         + " No additional job will be created")
            return
        self.scheduler.remove_job(job_id=vsiId)
        logging.info(f"CSMF Polling stopped for VSI {vsiId}")

    def my_listener(self, event):
        if e := event.exception:
            logging.warn(f"CSMF Polling for VSI {event.job_id} failed."
                         + f"Reason: {e}")
        else:
            print('The job worked :)')

    async def pollVsiLCM(self, vsiId):
        service_composition = await redis_handler.get_vsi_servicecomposition(
            vsiId
        )
        if service_composition:
            await self.poll_vsi_service_composition(vsiId, service_composition)

        primitives_running = await redis_handler.get_primitive_op_status(vsiId)
        if primitives_running:
            await self.poll_vsi_primitive_status(vsiId, primitives_running)
    
    async def poll_vsi_primitive_status(
        self,
        vsiId: int,
        data: Dict[str,
                   VerticalSchemas.PrimitiveStatus]):
        data_copy = copy.deepcopy(data)
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
                    actionId=primitive_id
                )
                msg = MessageSchemas.Message(
                    vsiId=vsiId,
                    msgType=Constants.TOPIC_FETCH_ACTION_INFO,
                    data=data.dict())

                await rabbit_handler.publish_queue(
                    Constants.QUEUE_DOMAIN,
                    json.dumps(msg.dict()))
        await redis_handler.store_primitive_op_status(vsiId,
                                                      data_copy,
                                                      parse_dict=True)
            
    async def poll_vsi_service_composition(
        self,
        vsiId: int,
        composition_data: Dict[str,
                               VerticalSchemas.ServiceComposition]):

        for component_name, data in composition_data.items():
            msg = MessageSchemas.Message(vsiId=vsiId)
            if data.sliceEnabled:
                msg.msgType = Constants.TOPIC_FETCH_NSI_INFO
                res_data = MessageSchemas.FecthNsiInfoData(
                    domainId=data.domainId,
                    nsiId=component_name
                )
            else:
                msg.msgType = Constants.TOPIC_FETCH_NS_INFO
                res_data = MessageSchemas.FetchNsInfoData(
                    domainId=data.domainId,
                    nsId=component_name
                )
            msg.data = res_data
            await rabbit_handler.publish_queue(
                Constants.QUEUE_DOMAIN,
                json.dumps(msg.dict()))


poller = Polling()