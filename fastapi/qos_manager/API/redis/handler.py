# @Author: Daniel Gomes
# @Date:   2022-09-21 15:41:48
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-22 23:25:25
import json
from typing import Dict
import aioredis
import aux.constants as Constants
from aux.startup import load_config

from schemas.primitive import PrimitiveStatus, ServiceComposition
import schemas.message as MessageSchemas
import schemas.auth as AuthSchemas

a = aioredis.from_url(
            f"redis://localhost",
            password="netorRedisPassword",
            port="6379"
        )
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

    async def start_transaction(self):
        return self.connector.multi_exec()
    async def get_all_vsi_data(self, vsiId):
        cached_vsi_data = await self.hget_all(vsiId)
        allVsiData = {}
        for key,value in cached_vsi_data.items():
            # load and parse data 
            key = key.decode()
            if key == Constants.TOPIC_TENANTINFO:
                allVsiData[key] = AuthSchemas.Tenant(
                    **json.loads(value)
            )
            else:
                allVsiData[key] = MessageSchemas.Message(
                    **json.loads(value))
        return allVsiData

    async def store_vsi_alarmfound(self, transaction, vsiId, value):
        print(vsiId, value)
        return await transaction.execute_command("hset",
            "alarmFound",
            vsiId,
            value
        )
    async def get_vsi_alarmfound(self,transaction, vsiId):
        return await transaction.hget("alarmFound", vsiId)

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
    
    async def get_all_service_composition(self):
        cached_data = await self.hget_all("serviceComposition")
        allVsiData = {}
        for key,value in cached_data.items():
            key = key.decode()
            allVsiData[key] = {k: ServiceComposition(**v) for k,v \
                    in json.loads(value).items()}
        return allVsiData

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
            if not store_objects:
                return data
            return {key: PrimitiveStatus(**value) for key,value \
                    in data.items()}
        
        return None
    async def tear_down_vsi_data(self, vsiId):
        await self.delete_key(vsiId)
        await self.delete_hash_key(Constants.TOPIC_CREATEVSI, vsiId)
        await self.delete_hash_key("serviceComposition", vsiId)
        await self.delete_hash_key("Primitive", vsiId)

redis_handler = RedisHandler()


