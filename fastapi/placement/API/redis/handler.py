# @Author: Daniel Gomes
# @Date:   2022-09-21 15:41:48
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-24 21:58:48
import aioredis
import aux.constants as Constants
from aux.startup import load_config

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
    
    # only when catalogue, domain and tenant information has been aggregated
    # we can proceed to the placement step

    async def has_required_placement_info(self, vsiId, data):
        create_vsi = await self.get_hash_value(
            Constants.TOPIC_CREATEVSI, vsiId)
        return create_vsi.decode() == "create" and \
               set(["catalogueInfo","domainInfo","tenantInfo"])\
               .issubset(data)
    
    async def store_vsi_initial_data(self, vsiId):
        await self.set_hash_key(
            Constants.TOPIC_CREATEVSI,
            vsiId,
            "create")
    
    async def update_vsi_running_data(self, vsiId):
        await self.set_hash_key(
            Constants.TOPIC_CREATEVSI,
            vsiId,
            "alreadyCreated"
            )
    
    async def tear_down_vsi_data(self, vsiId):
        await self.delete_key(vsiId)
        await self.delete_hash_key(Constants.TOPIC_CREATEVSI, vsiId)

redis_handler = RedisHandler()