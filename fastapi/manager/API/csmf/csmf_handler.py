# @Author: Daniel Gomes
# @Date:   2022-09-26 16:05:03
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-05 21:15:04

import aux.constants as Constants
from aux.enums import VSIStatus
from csmf.vsi_helper import vsi_helper
from csmf.polling import poller
from redis.handler import redis_handler
from rabbitmq.adaptor import rabbit_handler
import schemas.message as MessageSchemas
import schemas.vertical as VerticalSchemas
import sql_app.crud.csmf as CsmfCRUD
from sql_app.database import SessionLocal
from sqlalchemy.orm import Session
import aux.utils as Utils
from fastapi_events.handlers.local import local_handler
from fastapi_events.typing import Event
import json
import logging


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


class CSMF_Handler():
    def __init__(self) -> None:
        self.counter = 0
        # self.poller = poller

    def start(self):
        logging.info("Starting CSMF Poller...")
        poller.start_all_jobs()

    async def store_new_csmf(self, db: Session,
                             payload: MessageSchemas.Message):
        #  add VSI status on Cache
        await redis_handler.store_vsi_initial_data(payload.vsiId) 
        # Store Received Message on Cache
        await redis_handler.set_hash_key(
            payload.vsiId,
            payload.msgType,
            json.dumps(payload.dict(exclude_none=True, exclude_unset=True))
        )
        # Store in database
        CsmfCRUD.createCSMF(db, payload)
        # Create CSMF Polling CronJob,
        #  which will ask the Domain Service for Info 
        #  regarding the Vsi Services
        poller.start_vsi_polling_csmf(payload.vsiId)
        await Utils.store_tenant_data(
            caching=redis_handler,
            vsiId=payload.vsiId, tenantId=payload.tenantId)
        return

    # Handles catalogueInfo and domainInfo Messages
    @local_handler.register(event_name='event-*Info')
    async def handle_required_info(event: Event):
        _, event_args = event
        payload = event_args
        logging.info(f"Storing {payload.msgType} Info")
        await redis_handler.set_hash_key(
            payload.vsiId,
            payload.msgType,
            json.dumps(payload.dict())
        )

    # Handles PlacementInfo Message: to Start the Instantiation of a VSi
    @local_handler.register(event_name=Constants.TOPIC_PLACEMENTINFO)
    async def handle_vsi_instantiation(event: Event):
        _, event_args = event
        payload = event_args
        db = next(get_db())
        # Store Placement Info
        await redis_handler.set_hash_key(
            payload.vsiId,
            payload.msgType,
            json.dumps(payload.dict(exclude_none=True, exclude_unset=True))
        )
        logging.info(f"Stored placement Info for Vsi {payload.vsiId}")
        # Retrieve current stored data in Cache
        vsi_current_data = await redis_handler.get_hash_keys(payload.vsiId)
        parsed_info = [x.decode() for x in vsi_current_data]

        if not await redis_handler.has_required_vsi_instation_info(
                payload.vsiId, parsed_info):
            # throw exception
            return
        logging.info("VSi has necessary info, starting to instantiate..")

        CsmfCRUD.updateCSMFStatus(db, payload.vsiId, VSIStatus.INSTATIATING)
        await redis_handler.update_vsi_running_data(payload.vsiId)
        await vsi_helper.instantiateVSI(payload)
        return
    
    # Updates on Cache the Ids of the Resources created acording to the NFVOIds
    @local_handler.register(event_name=Constants.TOPIC_UPDATE_NFVO_IDS)
    async def handle_nfvo_ids_update(event: Event):
        _, event_args = event
        payload = event_args
        # UpdateResourcesNfvoIdsData Message
        nfvo_data = payload.data
        service_composition = await redis_handler.get_vsi_servicecomposition(
            payload.vsiId)
        # store servicecomposition on Cache
        if service_composition:
            stored_data = service_composition[nfvo_data.componentName]
            stored_data.nfvoId = nfvo_data.componentId
            service_composition[nfvo_data.componentName] = stored_data
        else:
            data = VerticalSchemas.ServiceComposition(
                nfvoId=payload.componentId)
            service_composition = {nfvo_data.componentName: data.dict()}

        await redis_handler.store_vsi_service_composition(
            payload.vsiId, service_composition, parse_dict=True
        )
        return

    # Handle NSI Status Messages from Domain

    @local_handler.register(event_name=Constants.TOPIC_NSI_INFO)
    async def handle_nsi_info_message(event: Event):
        _, event_args = event
        payload = event_args
        db = next(get_db())
        # NsiInfoData Message
        nsi_info_data = payload.data
        data = MessageSchemas.StatusUpdateData(status=nsi_info_data.nsiInfo)
        update_message = MessageSchemas.Message(
            vsiId=payload.vsiId,
            msgType=Constants.TOPIC_VSI_STATUS,
            message=f"New NSI Status from Vertical with Id {payload.vsiId}")
        update_message.data = data
        await rabbit_handler.publish_queue(
            Constants.QUEUE_COORDINATOR,
            json.dumps(update_message.dict())
        )
        if await Utils.verify_resource_operate_status(
                "running", nsidata=nsi_info_data):
            # check if there's already stored the service composition
            service_composition = await redis_handler.\
                get_vsi_servicecomposition(payload.vsiId)
            # Update Cache's Service Composition status
            if service_composition:
                stored_data = service_composition[nsi_info_data.nsiId]
                stored_data.status = Constants.INSTANTIATED_STATUS
                service_composition[nsi_info_data.nsiId] = stored_data
            else:
                data = VerticalSchemas.ServiceComposition(
                    status=Constants.INSTANTIATED_STATUS)
                service_composition = {nsi_info_data.nsiId: data.dict()}
            # parse object to dict again
            await redis_handler.store_vsi_service_composition(
                payload.vsiId, service_composition, parse_dict=True
            )
            logging.info(f"NSi {nsi_info_data.nsiId} of VSi {payload.vsiId},"
                         + "is now running..")
            # Update in DB as well (hmmm TODO: check later!)
            CsmfCRUD.updateCSMFStatus(
                db, payload.vsiId, VSIStatus.INSTANTIATED)
            # Update Cache's VSI Status
            await redis_handler.update_vsi_running_data(payload.vsiId,
                                                        already_running=True)

        elif await Utils.verify_resource_operate_status(
                "terminated", nsidata=nsi_info_data):
            await vsi_helper.tearDownComponent(
                payload.vsiId,
                nsi_info_data.nsiId
            )
            pass
        return
    
    # Prepares the execution of a primitive, send to domain the correct 
    # information to do so
    @local_handler.register(event_name=Constants.TOPIC_PRIMITIVE)
    async def handle_primitive_execution(event: Event):
        _, event_args = event
        payload, db = event_args
        # PrimitiveData Message
        _ = payload.data
        running = await redis_handler.is_vsi_running(vsiId=payload.vsiId)
        if not running:
            # throw exception
            pass
        await vsi_helper.prepare_primitive_exec(payload)
        return

    # Receives the Primitive Execution Status From Domain
    @local_handler.register(event_name=Constants.TOPIC_ACTION_RESPONSE)
    async def handle_primitive_status_response(event: Event):
        _, event_args = event
        payload, db = event_args
        primivite_data = payload.data
        running_actions = await redis_handler.get_primitive_op_status(
            payload.vsiId
        )
        stored_action_data = running_actions.get(str(primivite_data.actionId),
                                                 None)
        if stored_action_data:
            stored_action_data.nfvoId = primivite_data.nfvoId
            if stored_action_data.status != primivite_data.status:
                # send Message to coordinator, since there's a new state
                data = MessageSchemas.ActionUpdateData(
                    actionId=stored_action_data.actionId,
                    status=primivite_data.status,
                    output=primivite_data.output
                )
                msg = MessageSchemas.Message(
                    vsiId=payload.vsiId,
                    msgType=Constants.TOPIC_ACTION_STATUS,
                    data=data
                )
                logging.info("New Action State, sending to coordinator: "
                             + f"{msg.dict}")
                await rabbit_handler.publish_queue(
                    Constants.QUEUE_COORDINATOR,
                    json.dumps(msg.dict()))

            stored_action_data.status = primivite_data.status
            stored_action_data.output = primivite_data.output
        running_actions[primivite_data.actionId] = stored_action_data
        await redis_handler.store_primitive_op_status(
            payload.vsiId, running_actions, parse_dict=True
        )
        return

    @local_handler.register(event_name=Constants.TOPIC_REMOVEVSI)
    async def handle_vsi_removal(event: Event):
        _, event_args = event
        payload, db = event_args
        a = await Utils.is_csmf_data_stored(
            db,
            redis_handler,
            Constants.TOPIC_CREATEVSI, payload.vsiId
            )
        await vsi_helper.deleteVSI(payload)
        if not a:
            logging.info("Cannot Delete VSI, since it is not stored")
            return
        return


csmf_handler = CSMF_Handler()
