# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-13 12:09:58

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
from csmf.csmf_handler import csmf_handler
# import from parent directory
currentdir = os.path.dirname(os.path.abspath(
             inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from fastapi_events.middleware import EventHandlerASGIMiddleware
from fastapi_events.handlers.local import local_handler
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
Constants.EVENT_HANDLER_ID = id(app)
app.add_middleware(EventHandlerASGIMiddleware,
                   handlers=[local_handler],  # registering handler(s)
                   middleware_id=Constants.EVENT_HANDLER_ID)  # register custom middleware id

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
    for i in range(10):
        try:
            models.Base.metadata.create_all(bind=engine)
            Constants.MODELS_INITIALIZED = True
            break
        except Exception as e:
            print(f"entering..{e}")
            time.sleep(10)

    if not Constants.MODELS_INITIALIZED:
        exit(2)

    db = SessionLocal()

    # Store Initial Data in Database
    Startup.fill_database(db)
    csmf_handler.start()
    await rabbit_handler.start_pool()
    redis_handler.start_connection()
    message_receiver = MessageReceiver(
        messaging=rabbit_handler,
        caching=redis_handler)
    await message_receiver.start()
    # domainInfo = {"vsiId":"1","error":False, "msgType": "domainInfo", "message":"TestDomain", "data": {"domainIds":["ITAV"]}}
    # tenantInfo = {"vsiId": "1", "msgType": "tenantInfo", "data": {"username": "admin", "group": "user", "roles": ["ADMIN"]}, "error": False}
    # catalogueInfo = {"message": "Success", "vsiId": "1", "msgType": "catalogueInfo", "error": False, "data": {"vsd": {"tenant_id": "user", "associated_vsd_id": None, "domain_id": "ITAV", "vs_descriptor_id": "608ae08e063c52ff4d88f32f", "version": "1.0", "is_public": True, "nested_vsd_ids": {}, "service_constraints": [], "vs_blueprint_id": "608ae069063c52ff4d88f327", "name": "vsdTest", "sla": None, "management_type": "TENANT_MANAGED", "qos_parameters": {"peers": 2}}, "vs_blueprint_info": {"vs_blueprint": {"urllc_service_category": None, "end_points": [], "inter_site": True, "parameters": [{"parameter_id": "peers", "parameter_type": "number", "applicability_field": "interdomain", "parameter_name": "Peers", "parameter_description": "#Peers"}], "version": "version_1", "blueprint_id": "608ae069063c52ff4d88f327", "service_sequence": [], "translation_rules": [{"nsd_version": "1.0", "input": [{"parameter_id": "peers", "max_value": 5, "min_value": 1}], "nsd_id": "interdomain-ns", "nst_id": "interdomain_e2e_nst", "blueprint_id": "608ae069063c52ff4d88f327", "nsd_info_id": None, "ns_instantiation_level_id": None, "ns_flavour_id": None}], "name": "vsb-test", "description": None, "atomic_components": [], "configurable_parameters": [], "application_metrics": [], "connectivity_services": [], "embb_service_category": "URBAN_MACRO", "slice_service_type": "EMBB"}, "on_boarded_nst_info_id": [], "on_boarded_mec_app_package_info_id": [], "on_boarded_vnf_package_info_id": [], "owner": None, "active_vsd_id": ["VsDescriptor object"], "vs_blueprint_id": "608ae069063c52ff4d88f327", "name": "vsb-test", "vs_blueprint_version": "version_1", "on_boarded_nsd_info_id": []}, "nsts": [{"nst_name": "Interdomain Slice", "nsst": [{"nst_name": "Interdomain Slice Subnet", "nsst": [], "nsd_version": "1.0", "geographical_area_info_list": [], "nst_provider": "ITAV", "nsd_id": "interdomain_slice_nsd", "nst_id": "interdomain_nsst", "nst_version": "1.0", "nst_service_profile": {"latency": 100, "sST": "EMBB", "resource_sharing_level": None, "max_number_of_UEs": 1000, "coverage_area_TA_list": [], "service_profile_id": "interdomain_profile", "uRLLC_perf_req": [], "availability": 100.0, "pLMN_id_list": [], "eMBB_perf_req": [{"user_density": 100, "activity_factor": None, "exp_data_rate_DL": None, "area_traffic_cap_DL": None, "area_traffic_cap_UL": None, "uE_speed": 10, "coverage": None, "exp_data_rate_uL": None}], "uE_mobility_level": None}, "nsst_type": "NONE", "nsst_ids": []}, {"nst_name": "Interdomain Slice Subnet", "nsst": [], "nsd_version": "1.0", "geographical_area_info_list": [], "nst_provider": "ITAV", "nsd_id": "interdomain_slice_nsd", "nst_id": "interdomain_nsst", "nst_version": "1.0", "nst_service_profile": {"latency": 100, "sST": "EMBB", "resource_sharing_level": None, "max_number_of_UEs": 1000, "coverage_area_TA_list": [], "service_profile_id": "interdomain_profile", "uRLLC_perf_req": [], "availability": 100.0, "pLMN_id_list": [], "eMBB_perf_req": [{"user_density": 100, "activity_factor": None, "exp_data_rate_DL": None, "area_traffic_cap_DL": None, "area_traffic_cap_UL": None, "uE_speed": 10, "coverage": None, "exp_data_rate_uL": None}], "uE_mobility_level": None}, "nsst_type": "NONE", "nsst_ids": []}], "nsd_version": "1.0", "geographical_area_info_list": [], "nst_provider": "ITAV", "nsd_id": None, "nst_id": "interdomain_e2e_nst", "nst_version": "1.0", "nst_service_profile": {"latency": 100, "sST": "EMBB", "resource_sharing_level": None, "max_number_of_UEs": 1000, "coverage_area_TA_list": [], "service_profile_id": "interdomain_profile", "uRLLC_perf_req": [], "availability": 100.0, "pLMN_id_list": [], "eMBB_perf_req": [{"user_density": 100, "activity_factor": None, "exp_data_rate_DL": None, "area_traffic_cap_DL": None, "area_traffic_cap_UL": None, "uE_speed": 10, "coverage": None, "exp_data_rate_uL": None}], "uE_mobility_level": None}, "nsst_type": "NONE", "nsst_ids": ["interdomain_nsst", "interdomain_nsst"]}], "vsb_actions": [{"action_name": "Add Tunnel Peer", "action_id": "addpeer", "parameters": [{"parameter_type": "STRING", "parameter_id": "peer_network", "parameter_name": "Peer Network", "parameter_default_value": "10.0.0.0/24"}], "blueprint_id": "608ae069063c52ff4d88f327"}, {"action_name": "Fetch Tunnel Peer Info", "action_id": "getvnfinfo", "parameters": [], "blueprint_id": "608ae069063c52ff4d88f327"}]}}
    # placementInfo = {"vsiId": "1", "msgType": "placementInfo", "error": False, "message": "Success",  "data": [{"domainId": "ITAV", "sliceEnabled": True, "nstId": "interdomain_nst"}, {"domainId": "ITAV", "sliceEnabled": True, "nstId": "interdomain_nst"}]}
    # msg1 = MessageSchemas.Message(**catalogueInfo)
    # msg2 = MessageSchemas.Message(**tenantInfo)
    # msg3 = MessageSchemas.Message(**domainInfo)
    