
from typing import Union
from qos.utils import CRITICAL, WARNING, OKAY, parse_json_playbook_output, generate_action_id
import schemas.alarms as AlarmSchemas
import schemas.message as MessageSchemas
from polling.base_polling import BasePolling
from polling.mem_polling import MemPolling
from qos.vsiqosdata import VSIQoSData
import aux.constants as Constants
import logging
from rabbitmq.adaptor import rabbit_handler
from redis.handler import redis_handler
import json
import aux.utils as Utils

logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)

class QosManager:
    def __init__(self) -> None:
        self.vsis = {}      
        self.poller = MemPolling()
        self.ansible_primitive_name = "ansible_playbook"
        self.get_wg_data_primitive = "apply_new_route"
        
    def get_link_tag(self, data: AlarmSchemas.LinkAlarmData):
        for tag in data.notify_details.tags:
            if tag == "link":
               return data.notify_details.tags[tag]
    def get_vnf_member_index_tag(self, data: AlarmSchemas.LinkAlarmData):
        for tag in data.notify_details.tags:
            if tag == "vnf_member_index":
               return  data.notify_details.tags[tag]
    async def get_vsi_by_ns_id(self, ns_id):
        services = await redis_handler.get_all_service_composition()
        for vsi in services:
            vsi_services = services[vsi]
            print(vsi_services, type(vsi_services))
            for service in vsi_services:
                if vsi_services[service].nfvoId == ns_id:
                    print("FOUND VSI", vsi)
                    return vsi

    async def add_vsi(self, alarm: AlarmSchemas.LinkAlarmData, app):
        vnf_member_index = alarm.notify_details.tags['vnf_member_index']
        vsi_id = await self.get_vsi_by_ns_id(alarm.notify_details.tags['ns_id'])
        #svsi_id = vnf_member_index.split("_")[0]
        tag = alarm.notify_details.extra_labels['link']
        
        obj = VSIQoSData(
                vsi_id=vsi_id
        )
        if vsi_id not in self.vsis:
            self.vsis[vsi_id] = obj
            self.poller.start_vsi_polling(
                vsi_id
            )
        
       
        val = 1.2 / alarm.notify_details.threshold_value
        is_critical = self.vsis[vsi_id].is_critical_threshold(tag, val)
        
        # we need to avoid setting multiple route changes for the same vertical service
        # at the same time
        if is_critical:
            
            async with redis_handler.connector.pipeline(transaction=True) as pipe:
                try:
                    await pipe.watch("alarmFound")
                    alarm_found = await redis_handler.get_vsi_alarmfound(
                        pipe,
                        vsi_id)
                    logging.info(alarm_found)
                    if alarm_found and alarm_found.decode() == "1":
                        logging.info("alarm already found")
                        return
                    
                    logging.info(f"starting transaction for {tag}...")
                    await pipe.execute_command("hset",
                        "alarmFound",
                        vsi_id,
                        "1"
                        )
                    
                    #await redis_handler.store_vsi_alarmfound(pipe, vsi_id, "1")
                    logging.info("transaction sucessful..")
                except Exception as e:
                    logging.info(f"Failed to execute transaction: {e}")

                #await pipe.execute()
        tag = alarm.notify_details.extra_labels['link']
        logging.info(f"continuing {tag}...")
        self.vsis[vsi_id].add_link(
            tag=tag,
            alarm=alarm
        )
        message = await self.vsis[vsi_id].analyze_threshold(
            tag=tag,
            threshold=val)
        if message:
            logging.info("sent alarm TS")
            Utils.send_instantiation_ts(
                vsiId=int(vsi_id),
                domain=None,
                action="RECEIVED_ALARM_TS")
            await self.poller.update_primitive_data(
                vsiId=vsi_id,
                data=message.data
            )
            await rabbit_handler.publish_queue(
                    Constants.QUEUE_DOMAIN,
                    json.dumps(message.dict()))
            # TODO: Change this to store in redis like a state machine
            self.vsis[vsi_id].is_route_change_starting = True
            

    async def apply_new_route(
        self,
        vsi_id,
        output:  Union[MessageSchemas.ActionResponseData, MessageSchemas.ActionNsData]):
        
        vsi_qos_obj = self.vsis[vsi_id]
        alarm_data = vsi_qos_obj.get_alarm_data_by_action_id(
            output.actionId
        )
        alarm_obj = alarm_data['alarm']
        service = await vsi_qos_obj.get_service_composition_by_ns_id(
            ns_id=alarm_obj.notify_details.tags['ns_id']
        )
        path = alarm_data['path']
        print("path", path)
        src_node, dest_node = path[0], path[-1]
        parsed_output = parse_json_playbook_output(output=output.output)
        new_routes_params = {
            'interface': 'wg0',
            'routes': {}
        }
        for i in range(len(path)):
            if i == len(path) - 1:
                new_routes_params['routes'][path[i]] = {}
                continue
            new_routes_params['routes'][path[i]] = {
                'dest_network': parsed_output,
                'gateway': path[i+1],
                'interface': 'wg0'}
        print("routes", new_routes_params)
        additionalConf = MessageSchemas.AdditionalConf(
            member_vnf_index= alarm_obj.notify_details.tags['vnf_member_index'],
            vdu_id="tunnel-as-a-service-sd",
            primitive=self.ansible_primitive_name,
            primitive_params={
                'playbook-name': self.get_wg_data_primitive,
                'route_data': json.dumps(new_routes_params)
            }

        )
        _uuid = generate_action_id()
        action = MessageSchemas.ActionNsData(
            primitiveName=self.ansible_primitive_name,
            domainId=service.domainId,
            nsId=alarm_obj.notify_details.tags['ns_id'],
            actionId=alarm_obj.notify_details.alarm_uuid,
            additionalConf=additionalConf,
            isAlarm=True
        )
        msg = MessageSchemas.Message(
            vsiId=vsi_id,
            msgType=Constants.TOPIC_ACTION_NS,
            data=action
        )
        vsi_qos_obj.is_route_change_starting = False
        #trn = redis.start_transaction()
        return msg
        # choose first node as the coordinator
            
            

qos_manager = QosManager()
    # invoke day-2 primitive to get the routes for a specific link in each VNF? too slow? need to know current context? too slow probably!
    # -> needs to retrieve VNF's data interface IP used in wireguard
    # Perhaps go to wireguard's allowed networks and compare agains tunnel peer address?


    # A -> B -> C -> D


    