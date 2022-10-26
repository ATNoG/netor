# @Author: Daniel Gomes
# @Date:   2022-09-28 11:32:59
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-26 23:24:51
import json
from manager.API.csmf.polling import Polling
from redis.handler import redis_handler
from rabbitmq.adaptor import rabbit_handler
import schemas.message as MessageSchemas
import schemas.vertical as VerticalSchemas
import yaml
import aux.constants as Constants
import aux.utils as Utils
import logging

logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)

class VsiHelper:
    def __init__(self) -> None:
        pass
    
    def is_a_slice(self, data: MessageSchemas.PlacementInfoData):
        return data.sliceEnabled and data.nstId

    def is_interdomain(self, cat_data: MessageSchemas.CatalogueInfoData):
        return cat_data.vs_blueprint_info.vs_blueprint.inter_site

    def default_value_exists(self, param, additional_conf):

        return "parameter_default_value" in param \
                and param['parameter_default_value']\
                and param['parameter_id'] \
                not in additional_conf.primitive_params

    async def instantiateVSI(self, payload: MessageSchemas.Message):
        cached_vsi_data = await redis_handler.hget_all(payload.vsiId)
        allVsiData = {}
        for key,value in cached_vsi_data.items():
            # load and parse data 
            allVsiData[key.decode()] = MessageSchemas.Message(
                **json.loads(value))
            if allVsiData[key.decode()].error:
                #raise InvalidPlacementInformation()
                pass
        domainInfo = allVsiData['domainInfo']
        vsiRequestInfo = allVsiData['createVSI']
        catalogueInfo = allVsiData['catalogueInfo']
        placementInfo = payload.data
        res = MessageSchemas.Message(vsiId=payload.vsiId)
        composingComponentId = 1
        for placement in placementInfo:
            component_name = f"{payload.vsiId}_{composingComponentId}"\
                             + f"-{vsiRequestInfo.data.name}"
            data = None
            if self.is_a_slice(placement):
                data = MessageSchemas.InstantiateNsiData(
                    name=component_name,
                    description=vsiRequestInfo.data.description,
                    domainId=placement.domainId,
                    nstId=placement.nstId
                    )
                res.msgType = Constants.TOPIC_INSTANTIATE_NSI
                if self.is_interdomain(catalogueInfo.data):
                    config = None
                    for conf_component in vsiRequestInfo.data.additionalConf:
                        #TODO: check better component name verification
                        if conf_component['componentName'] == component_name:
                            config = json.loads(conf_component['conf'])
                            data.additionalConf = yaml.safe_dump(config)
                            break
            # store on redis VSI Service Composition
            serviceComposition = await redis_handler.get_vsi_servicecomposition(
                vsiId=payload.vsiId, store_objects=False
            )

            composition_data = VerticalSchemas.ServiceComposition(
                sliceEnabled=placement.sliceEnabled,
                domainId=placement.domainId,
                status=Constants.INSTANTIATING_STATUS
                )

            if not serviceComposition:
                serviceComposition = {component_name: composition_data.dict(
                    exclude_unset=True,
                )}
            else:
                serviceComposition[component_name] = composition_data.dict(
                    exclude_unset=True,
                )
            logging.info(f"Service Composition: {serviceComposition}")
            await redis_handler.store_vsi_service_composition(
                vsiId=payload.vsiId,
                data=serviceComposition
            )
            res = Utils.prepare_message(res, data)
            # send message to Domain to instantiatie each component
            await rabbit_handler.publish_queue(
                Constants.QUEUE_DOMAIN,
                json.dumps(res.dict()))
            composingComponentId+=1 #TODO: Check this, will be changed...


        res.msgType = Constants.TOPIC_VSI_STATUS
        data = MessageSchemas.StatusUpdateData(
            status=Constants.DEPLOYING_STATUS
        )
        res = Utils.prepare_message(res, data, 
            msg="Sent all instantiation requests to the appropriate domains")
        await rabbit_handler.publish_queue(
            Constants.QUEUE_COORDINATOR,
            json.dumps(res.dict())
        )
        
    
    async def prepare_primitive_exec(self, payload: MessageSchemas.Message):
        primivite_data = payload.data
        allVsiData = await redis_handler.get_all_vsi_data(payload.vsiId)
        service_composition = await redis_handler.\
                get_vsi_servicecomposition(payload.vsiId)
        catalogueInfo = allVsiData['catalogueInfo']
        cat_data = catalogueInfo.data
        actions = {x['action_id']: x['parameters'] for x in cat_data.vsb_actions}

        if primivite_data.primitiveName not in actions:
            # raise excpetion, invalid primitive
            return

        if primivite_data.primitiveTarget not in service_composition:
            #raise exception, invalid primitive, not running yet
            return
        service = service_composition[primivite_data.primitiveTarget]
        if service.sliceEnabled:
            #TODO: processing with the Subnet NS Id because 
            # OSM currently doesn't support NSI actions
            pass
        
        additional_conf = MessageSchemas.AdditionalConf(
            member_vnf_index=primivite_data.primitiveInternalTarget,
            primitive=primivite_data.primitiveName,
            primitive_params=primivite_data.primitiveParams
        )
        for param in actions[primivite_data.primitiveName]:
            # if catalogue contains parameters with default values
            # then the config data will be fullfilled
            if self.default_value_exists(param, additional_conf):
                additional_conf.primitive_params[param['parameter_id']] \
                        = param['parameter_default_value']
            
        message_data = MessageSchemas.ActionNsData(
            primitiveName=primivite_data.primitiveName,
            domainId=service.domainId,
            nsId=service.nfvoId,
            additionalConf=additional_conf
        )
        message = MessageSchemas.Message(
            vsiId=payload.vsiId,
            msgType=Constants.TOPIC_ACTION_NS,
            data=message_data
            )
        logging.info("Sending Message to Domain to Start executing primitive")
        await rabbit_handler.publish_queue(
            Constants.QUEUE_DOMAIN, json.dumps(message.dict()))
        
        #Store new primitive data on Cache to later fetch from Domain the op
        # execution status
        action_data = VerticalSchemas.PrimitiveStatus(
            actionId=primivite_data.actionId,
            domainId=service.domainId,
            nfvoId="5d7bc1b5-7e38-49f7-a3ec-848dfc4525e8"
        )
        running_actions = await redis_handler.get_primitive_op_status(
            payload.vsiId, store_objects=False)
        
        if not running_actions:
            actions = {primivite_data.actionId: action_data.dict(
                exclude_unset=True,
            )}
        else:
            actions[primivite_data.actionId] = action_data.dict(
                exclude_unset=True,
            )
            
        logging.info(f"Storing on Redis Primitive Operational Status.. {actions}")
        await redis_handler.store_primitive_op_status(
            payload.vsiId, actions
        )
    async def deleteVSI(self, payload: MessageSchemas.Message):
        serviceComposition = await redis_handler.get_vsi_servicecomposition(
                vsiId=payload.vsiId)
        msg_domain = MessageSchemas.Message(
            vsiId=payload.vsiId
        )
        force = payload.data.force
        logging.info("Deleting VSI Data...")
        for component, componentData in serviceComposition.items():
            componentData.status = Constants.TERMINATING_STATUS
            if componentData.sliceEnabled:
                data = MessageSchemas.DeleteNsiData(
                    domainId=componentData.domainId,
                    nsiId=componentData.nsiId,
                    force=force
                )
                topic = Constants.TOPIC_DELETE_NSI
            else:
                data = MessageSchemas.DeleteNsData(
                    domainId=componentData.domainId,
                    nsiId=componentData.nsiId,
                    force=force   
                )
                topic = Constants.TOPIC_DELETE_NS
            msg = Utils.prepare_message(msg_base=msg_domain,
                                        data=data,
                                        msgType=topic)
            logging.info("Send Terminate Action to Domain for component")
            await rabbit_handler.publish_queue(
                Constants.QUEUE_DOMAIN,
                json.dumps(msg.dict())
            )
        # store update in component status
        await redis_handler.store_vsi_service_composition(
            payload.vsiId,
            data=serviceComposition,
            parse_dict=True
        )
        update_data = MessageSchemas.StatusUpdateData(
            status=Constants.TERMINATING_STATUS
        )
        lcm_message = MessageSchemas.Message(
            vsiId=payload.vsiId,
            message="Terminating Vertical Service Instance",
            data=update_data
        )
        await rabbit_handler.publish_queue(
            Constants.QUEUE_COORDINATOR,
            json.dumps(lcm_message.dict())
        )

        #TODO: Perhap delete Here
    

    async def tearDownComponent(self, vsiId, componentName, polling: Polling):
        serviceComposition = await redis_handler.get_vsi_servicecomposition(
            vsiId=vsiId,
            store_objects=True
        )
        if componentName in serviceComposition:
            serviceComposition[componentName].status = Constants.\
                                                        TERMINATED_STATUS
        all_terminated = all([
            (x,y) for (x,y) in serviceComposition.items() \
            if y.status == Constants.TERMINATED_STATUS
        ])    
        if all_terminated:
            logging.info("All Components terminated, deleting Vsi Data")
            await redis_handler.tear_down_vsi_data(vsiId=vsiId)
            await polling.stop_vsi_polling_csmf(vsiId=vsiId)
        
        update_data = MessageSchemas.StatusUpdateData(
            status=Constants.TERMINATED_STATUS
        )
        lcm_message = MessageSchemas.Message(
            vsiId=vsiId,
            message="Terminated Vertical Service Instance",
            data=update_data
        )
        await rabbit_handler.publish_queue(
            Constants.QUEUE_COORDINATOR,
            json.dumps(lcm_message.dict())
        )

        


vsi_helper = VsiHelper()

        