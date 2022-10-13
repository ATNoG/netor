# @Author: Daniel Gomes
# @Date:   2022-09-21 15:41:48
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-12 17:09:52
import json
from typing import Dict
import aioredis
import aux.constants as Constants
from aux.startup import load_config

from aux.enums import VSIStatus
from schemas.vertical import PrimitiveStatus, ServiceComposition
import schemas.message as MessageSchemas


class RedisHandler:
    def __init__(self) -> None:
        load_config()

        self.uri = f"redis://{Constants.REDIS_IP}"
        self.connector = None

    def start_connection(self):
        self.connector = aioredis.from_url(
            self.uri,
            password=Constants.REDIS_PASS,
            port=Constants.REDIS_PORT
        )
    
    async def hget_all(self, mainkey):
        return await self.connector.hgetall(mainkey)

    async def get_hash_keys(self, mainkey):
        return await self.connector.hkeys(mainkey)

    async def set_hash_key(self, mainkey,key,value):
        return await self.connector.hset(mainkey,key, value)

    async def get_hash_value(self, mainkey, key):
        return await self.connector.hget(mainkey,key)

    async def delete_hash_key(self, mainKey, key):
        return await self.connector.hdel(mainKey, key)

    async def delete_key(self, mainKey):
        return await self.connector.delete(mainKey)

    # only when catalogue, domain, placement and tenant information has been aggregated
    # we can proceed to the placement step
    async def has_required_vsi_instation_info(self, vsiId, data):
        create_vsi = await self.get_hash_value(
            Constants.TOPIC_CREATEVSI, vsiId)
        if not create_vsi:
            return False
        return create_vsi.decode() == VSIStatus.CREATED.value and \
               set(["catalogueInfo","domainInfo","tenantInfo", "placementInfo"])\
               .issubset(data)
    
    async def is_vsi_running(self, vsiId):
        create_vsi = await self.get_hash_value(
            Constants.TOPIC_CREATEVSI, vsiId)
        if create_vsi:
            decoded_val = create_vsi.decode()
            return decoded_val == VSIStatus.INSTANTIATED.value
        return False
    async def store_vsi_initial_data(self, vsiId):
        await self.set_hash_key(
            Constants.TOPIC_CREATEVSI,
            vsiId,
            VSIStatus.CREATED.value)
    
    async def update_vsi_running_data(self, vsiId, already_running=False):
        status = VSIStatus.INSTATIATING.value
        if already_running:
            status = VSIStatus.INSTANTIATED.value
        await self.set_hash_key(
            Constants.TOPIC_CREATEVSI,
            vsiId,
            status
            )
    async def get_all_vsi_data(self, vsiId):
        cached_vsi_data = await self.hget_all(vsiId)
        allVsiData = {}
        for key,value in cached_vsi_data.items():
            # load and parse data 
            allVsiData[key.decode()] = MessageSchemas.Message(
                **json.loads(value))
        return allVsiData

    async def store_vsi_service_composition(self, vsiId, data, parse_dict=False):
        if parse_dict:
            # parse object to dict again
            data = {x: y.dict()
                               for x,y in data.items()}
        return await self.set_hash_key(
            "serviceComposition",
            vsiId,
            json.dumps(data)    
        )
    async def get_vsi_servicecomposition(self, vsiId, store_objects=True):
        data = await self.get_hash_value(
            "serviceComposition",
            vsiId
        )
        if data:
            data = json.loads(data)
            if not store_objects:
                return data
            return {key: ServiceComposition(**value) for key,value \
                    in data.items()}
        return None
    
    
    async def store_primitive_op_status(self, vsiId, data, parse_dict=False):
        if parse_dict:
            # parse object to dict again
            data = {x: y.dict()
                               for x,y in data.items()}
        await self.set_hash_key(
            "Primitive",
            vsiId,
            json.dumps(data)
        )
    async def get_primitive_op_status(self, vsiId, store_objects=True):
        data = await self.get_hash_value(
            "Primitive",
            vsiId
        )
        if data:
            data = json.loads(data.decode())
            print("DATA", data, type(data))
            if not store_objects:
                return data
            return {key: PrimitiveStatus(**value) for key,value \
                    in data.items()}
        
        return None
    async def tear_down_vsi_data(self, vsiId):
        await self.delete_key(vsiId)
        await self.delete_hash_key(Constants.TOPIC_CREATEVSI, vsiId)

redis_handler = RedisHandler()


