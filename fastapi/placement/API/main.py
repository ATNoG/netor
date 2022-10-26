# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-13 12:09:29

import json
from fastapi import FastAPI
import logging
import inspect
import sys
import os
import time
# custom imports
from sql_app import models
from sql_app.database import SessionLocal, engine
from rabbitmq.adaptor import rabbit_handler
import aux.constants as Constants
import schemas.message as MessageSchemas
from rabbitmq.messaging_manager import MessageReceiver
import aux.startup as Startup
from redis.handler import redis_handler
# import from parent directory
currentdir = os.path.dirname(os.path.abspath(
             inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


# Start Fast API
app = FastAPI(
    title="FastAPI Base Project",
    description="A base Project of FastAPI",
    version="0.0.1",
    contact={
        "name": "User",
        "email": "user@av.it.pt",
    },
)
# app.add_middleware(
#     CORSMiddleware,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )



# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():

    # Load Config
    ret, message = Startup.load_config()
    if not ret:
        logging.critical(message)
        return exit(1)

    # Connect to Database
    MODELS_INITIALIZED = False
    for i in range(10):
        try:
            models.Base.metadata.create_all(bind=engine)
            MODELS_INITIALIZED = True
            break
        except Exception as e:
            print(f"entering..{e}")
            time.sleep(10)

    if not MODELS_INITIALIZED:
        exit(2)

    db = SessionLocal()

    # Store Initial Data in Database
    Startup.fill_database(db)
    a = "{\"vsiId\": \"0\", \"msgType\": \"catalogueInfo\", \"message\": \"Success\", \"error\": false, \"data\": {\"vs_blueprint_info\": {\"vs_blueprint\": {\"end_points\": [], \"inter_site\": true, \"parameters\": [{\"parameter_id\": \"peers\", \"parameter_type\": \"number\", \"applicability_field\": \"interdomain\", \"parameter_name\": \"Peers\", \"parameter_description\": \"#Peers\"}], \"version\": \"version_1\", \"blueprint_id\": \"6357a09544823943625b770c\", \"service_sequence\": [], \"translation_rules\": [{\"nsd_version\": \"1.0\", \"input\": [{\"parameter_id\": \"peers\", \"max_value\": 10, \"min_value\": 1}], \"nst_id\": \"interdomain_e2e_nstNST\", \"blueprint_id\": \"6357a09544823943625b770c\"}], \"name\": \"vsb-testNST\", \"atomic_components\": [], \"configurable_parameters\": [], \"application_metrics\": [], \"connectivity_services\": [], \"embb_service_category\": \"URBAN_MACRO\", \"slice_service_type\": \"EMBB\"}, \"on_boarded_nst_info_id\": [], \"on_boarded_mec_app_package_info_id\": [], \"on_boarded_vnf_package_info_id\": [], \"active_vsd_id\": [\"VsDescriptor object\"], \"vs_blueprint_id\": \"6357a09544823943625b770c\", \"name\": \"vsb-testNST\", \"vs_blueprint_version\": \"version_1\", \"on_boarded_nsd_info_id\": []}, \"vsd\": {\"tenant_id\": \"admin\", \"domain_id\": \"ITAV\", \"vs_descriptor_id\": \"6357a09a44823943625b771b\", \"version\": \"1.0\", \"is_public\": true, \"nested_vsd_ids\": {}, \"service_constraints\": [], \"vs_blueprint_id\": \"6357a09544823943625b770c\", \"name\": \"vsdTestNST\", \"management_type\": \"TENANT_MANAGED\", \"qos_parameters\": {\"peers\": \"4\"}}, \"nsts\": [{\"nst_name\": \"Interdomain Slice NST\", \"nsd_version\": \"1.0\", \"geographical_area_info_list\": [], \"nst_provider\": \"ITAV\", \"nst_id\": \"interdomain_e2e_nstNST\", \"nst_version\": \"1.0\", \"nst_service_profile\": {\"latency\": 100, \"sST\": \"EMBB\", \"max_number_of_UEs\": 1000, \"coverage_area_TA_list\": [], \"service_profile_id\": \"interdomain_profile\", \"uRLLC_perf_req\": [], \"availability\": 100.0, \"pLMN_id_list\": [], \"eMBB_perf_req\": [{\"activity_factor\": null, \"uE_speed\": 10, \"user_density\": 100, \"exp_data_rate_DL\": null, \"exp_data_rate_uL\": null, \"coverage\": null, \"area_traffic_cap_UL\": null, \"area_traffic_cap_DL\": null}]}, \"nsst_type\": \"NONE\", \"nsst_ids\": [\"tunnel-as-a-service-sd-nst\", \"tunnel-as-a-service-sd-nst\"], \"nsst\": []}], \"vsb_actions\": [{\"action_name\": \"Add Tunnel Peer\", \"action_id\": \"add-peer\", \"parameters\": [{\"parameter_name\": \"Peer Endpoint\", \"parameter_id\": \"peer_endpoint\", \"parameter_type\": \"STRING\", \"parameter_default_value\": null}, {\"parameter_name\": \"Peer Public Key\", \"parameter_id\": \"peer_public_key\", \"parameter_type\": \"STRING\", \"parameter_default_value\": null}, {\"parameter_name\": \"Peer Allowed Netorks\", \"parameter_id\": \"allowed_networks\", \"parameter_type\": \"STRING\", \"parameter_default_value\": \"null\"}], \"blueprint_id\": \"6357a09544823943625b770c\"}, {\"action_name\": \"Route Management\", \"action_id\": \"ip-route-management\", \"parameters\": [{\"parameter_name\": \"Network\", \"parameter_id\": \"network\", \"parameter_type\": \"STRING\", \"parameter_default_value\": null}, {\"parameter_name\": \"Action to be executed\", \"parameter_id\": \"action\", \"parameter_type\": \"STRING\", \"parameter_default_value\": null}, {\"parameter_name\": \"Gateway Address\", \"parameter_id\": \"gw_address\", \"parameter_type\": \"STRING\", \"parameter_default_value\": null}], \"blueprint_id\": \"6357a09544823943625b770c\"}, {\"action_name\": \"Get Wireguard Base Info\", \"action_id\": \"get-wireguard-base-info\", \"parameters\": [], \"blueprint_id\": \"6357a09544823943625b770c\"}, {\"action_name\": \"Get VNF Ips\", \"action_id\": \"get-vnf-ip\", \"parameters\": [], \"blueprint_id\": \"6357a09544823943625b770c\"}, {\"action_name\": \"Get Peers\", \"action_id\": \"get-peers\", \"parameters\": [{\"parameter_name\": \"Peer Endpoint IP\", \"parameter_id\": \"peer_endpoint_ip\", \"parameter_type\": \"STRING\", \"parameter_default_value\": \"null\"}, {\"parameter_name\": \"Peer Public Key\", \"parameter_id\": \"peer_public_key\", \"parameter_type\": \"STRING\", \"parameter_default_value\": \"null\"}], \"blueprint_id\": \"6357a09544823943625b770c\"}, {\"action_name\": \"Update Peer Endpoit\", \"action_id\": \"update-peer-endpoint\", \"parameters\": [{\"parameter_name\": \"Peer Endpoint IP\", \"parameter_id\": \"peer_endpoint_ip\", \"parameter_type\": \"STRING\", \"parameter_default_value\": \"null\"}, {\"parameter_name\": \"Peer Public Key\", \"parameter_id\": \"peer_public_key\", \"parameter_type\": \"STRING\", \"parameter_default_value\": \"null\"}, {\"parameter_name\": \"New Endpoint\", \"parameter_id\": \"new_endpoint\", \"parameter_type\": \"STRING\", \"parameter_default_value\": null}], \"blueprint_id\": \"6357a09544823943625b770c\"}, {\"action_name\": \"Update wireguard's server IP\", \"action_id\": \"update-wg-ip\", \"parameters\": [{\"parameter_name\": \"Wireguard New IP\", \"parameter_id\": \"wg_new_ip\", \"parameter_type\": \"STRING\", \"parameter_default_value\": null}], \"blueprint_id\": \"6357a09544823943625b770c\"}, {\"action_name\": \"Update Peer Allowed IPs\", \"action_id\": \"update-peer-allowed-ips\", \"parameters\": [{\"parameter_name\": \"Peer Endpoint IP\", \"parameter_id\": \"peer_endpoint_ip\", \"parameter_type\": \"STRING\", \"parameter_default_value\": \"null\"}, {\"parameter_name\": \"Peer Public Key\", \"parameter_id\": \"peer_public_key\", \"parameter_type\": \"STRING\", \"parameter_default_value\": \"null\"}, {\"parameter_name\": \"Action (add/remove)\", \"parameter_id\": \"action\", \"parameter_type\": \"STRING\", \"parameter_default_value\": null}, {\"parameter_name\": \"Network to be added to the allowed IPs\", \"parameter_id\": \"network\", \"parameter_type\": \"STRING\", \"parameter_default_value\": null}], \"blueprint_id\": \"6357a09544823943625b770c\"}, {\"action_name\": \"Delete Peer, given its Endpoint IP or Public Key\", \"action_id\": \"delete-peer\", \"parameters\": [{\"parameter_name\": \"Peer Endpoint IP\", \"parameter_id\": \"peer_endpoint_ip\", \"parameter_type\": \"STRING\", \"parameter_default_value\": \"null\"}, {\"parameter_name\": \"Peer Public Key\", \"parameter_id\": \"peer_public_key\", \"parameter_type\": \"STRING\", \"parameter_default_value\": \"null\"}], \"blueprint_id\": \"6357a09544823943625b770c\"}, {\"action_name\": \"Get Wireguard's Network Routes\", \"action_id\": \"get-ip-routes\", \"parameters\": [], \"blueprint_id\": \"6357a09544823943625b770c\"}]}}"
    a = json.loads(a)
    b = MessageSchemas.Message(**a)
    print(b.dict())
    await rabbit_handler.start_pool()
    redis_handler.start_connection()
    message_receiver = MessageReceiver(
        messaging=rabbit_handler,
        caching=redis_handler)
    await message_receiver.start()