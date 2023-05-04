
import schemas.alarms as AlarmSchemas
import schemas.message as MessageSchemas
from qos.utils import CRITICAL, WARNING
from qos.utils import generate_action_id, update_object
from qos.dijkstra import dijkstra
from redis.handler import redis_handler
import logging
import aux.constants as Constants
import os
import inspect

currentdir = os.path.dirname(os.path.abspath(
             inspect.getfile(inspect.currentframe())))

logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)

class VSIQoSData:
    def __init__(self, vsi_id) -> None:
        self.vsi_id = vsi_id
        self.links = {}
        self.alarms_data = {}
        # used to store the paths that the routes should take
        self.paths = {}
        self.ansible_primitive_name = "ansible_playbook"
        self.get_wg_data_primitive = "get_allowed_networks"
        self.is_route_change_starting = False
    
    def add_link(self, tag, alarm):
        src_ip, dest_ip = tag.split("_")
        val = 0.9 / alarm.notify_details.threshold_value
        if src_ip not in self.links:
            self.links[src_ip] = {dest_ip: val}
        else:
            self.links[src_ip][dest_ip] = val
        if not f'{src_ip}_{dest_ip}' in self.alarms_data:
            self.alarms_data[f'{src_ip}_{dest_ip}'] = {'alarm': alarm}
        else:
            old_obj = self.alarms_data[f'{src_ip}_{dest_ip}']['alarm']
            new_obj = update_object(old_obj, alarm)
            self.alarms_data[f'{src_ip}_{dest_ip}']['alarm'] = new_obj
        logging.info(f"links: {self.links}")
        logging.info(f"alarms data: {self.alarms_data}")
    
    async def get_service_composition_by_ns_id(self, ns_id):
        services = await redis_handler.get_vsi_servicecomposition(
            self.vsi_id, store_objects=True
        )
        for k, v in services.items():
            if v.nfvoId == ns_id:
                return services[k]
    def is_critical_threshold(self, tag, threshold):
        return threshold <= WARNING
    
    async def analyze_threshold(self, tag, threshold):
        src, dest = tag.split("_")
        if self.is_critical_threshold(tag, threshold):
            logging.info("Critical threshold found.. deciding new route to apply")
            return await self.decide_new_route(src, dest)
        else:
            pass
    
    def get_dest_node_alarm_data(self, dest_ip):
        for link in self.alarms_data:
            if f"{dest_ip}_" in link:
                return self.alarms_data[link]['alarm'].notify_details



    def get_alarm_data_by_action_id(self, action_id):
        action_id = str(action_id)
        for link in self.alarms_data:
            alarm = self.alarms_data[link]['alarm']
            if alarm.actionId == action_id:
                return self.alarms_data[link]

    async def decide_new_route(self, src, dest):
        message = None
        #app.state.lock.acquire()
        
        path = dijkstra(
            self.links,
            src,
            dest
        )
        print(path)
        src_node, dest_node = path[0], path[-1]
        dest_alarm_data = self.get_dest_node_alarm_data(dest_ip=dest_node)
        ns_id = dest_alarm_data.tags['ns_id']
        service = await self.get_service_composition_by_ns_id(
            ns_id=ns_id
        )
        #any alarm whose link prefix is equal to the destination node
        # will have its ns_id

        dest_network = None
        additionalConf = MessageSchemas.AdditionalConf(
            member_vnf_index= dest_alarm_data.tags['vnf_member_index'],
            primitive=self.ansible_primitive_name,
            vdu_id="tunnel-as-a-service-sd",
            primitive_params={
                'playbook-name': self.get_wg_data_primitive,
                'route_data': ''
            }

        )
        alarm_uuid = self.alarms_data[f'{src_node}_{dest_node}']['alarm']\
                        .notify_details.alarm_uuid
        _uuid = generate_action_id()
        action = MessageSchemas.ActionNsData(
            isAlarm=True,
            primitiveName=self.ansible_primitive_name,
            domainId=service.domainId,
            nsId=ns_id,
            actionId=_uuid,
            additionalConf=additionalConf
        )
        message = MessageSchemas.Message(
        vsiId=self.vsi_id,
        msgType=Constants.TOPIC_ACTION_NS,
        data=action
        )
        logging.info(f"Message {message}")
        # store the path
        self.alarms_data[f'{src_node}_{dest_node}']['path'] = path
        # update the action Id of the alarm stored
        self.alarms_data[f'{src_node}_{dest_node}']['alarm'].actionId = _uuid
        #app.state.alarm_processed = True

        return message


        # this action will query the destination node and have as argument
        # the node's internal wg network ( to differ in the allowed networks)
        # the output will the  "mgmt/data" network used in Wireguard
        # as well as the wg_config of the remaingin peers
        # actionId = self.driver.sendActionNS(
        #     nsId=s,
        #     additionalConf={"get_wg_route_data..": ""}
        # )
        # # wait some time to execute the action...
        # time.sleep(0.5)
        # output = self.driver.get_primitive_state(
        #     actionId
        # )['detailed-status']

        # {
        #     "action": "primitive",
        #     "primitiveName":"get-wireguard-base-info",
        #     "primitiveTarget":"1_1-wireguard",
        #     "primitiveInternalTarget":"1",
        #     "primitiveParams":{
        #     }
        # }
        # output = parse_json_playbook_output(
        #     output=output)
        # # perhaps will need another day-2 action to retrieve the public keys..
        # payload = {}
        # for i in range(path):
        #     node = path[i]
        #     nfvoId = self.nfvo_ids[node]
        #     if i == len(path) - 1:
        #         continue       
        #     route = {
        #         'dest_network':  output.strip(),
        #         'gateway': path[i+1],
        #         'interface': 'wg0'
        #     }
    