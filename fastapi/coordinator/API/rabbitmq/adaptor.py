# -*- coding: utf-8 -*-
# @Author: (your name)
# @Date:   2022-08-16 15:02:07
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-19 16:55:40

import aux.constants as Constants
from aio_pika import connect_robust, Channel, Message, ExchangeType
from aio_pika.pool import Pool
import logging
from aux.startup import load_config
logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)


class RabbitHandler:
    def __init__(self) -> None:
        load_config()
        self.uri = f"amqp://" \
                        f"{Constants.RABBITMQ_USER}:{Constants.RABBITMQ_PASS}"\
                        f"@{Constants.RABBITMQ_IP}:{Constants.RABBITMQ_PORT}"
        self.connection_pool = None
        self.channel_pool = None
        self.exchange = None
        self.queue = None
   
    async def start_pool(self):
        self.connection_pool = Pool(self.get_connection, max_size=2)
        self.channel_pool = Pool(self.get_channel, max_size=10)
        logging.info("Starting pool....")

    async def get_connection(self):
        return await connect_robust(self.uri)
    
    async def get_channel(self) -> Channel:
        if self.connection_pool:
            async with self.connection_pool.acquire() as connection:
                return await connection.channel()

    async def create_exchange(self, name):
        async with self.channel_pool.acquire() as channel:  # type: Channel
            await channel.declare_exchange(
                name, ExchangeType.FANOUT, auto_delete=True
            )
            logging.info(f"Created Exchange {name}...")

    async def create_queue(self, name, durable=False, auto_delete=True):
        async with self.channel_pool.acquire() as channel:
            await channel.declare_queue(
                name=name,
                durable=durable,
                auto_delete=auto_delete
            )
            logging.info(f"Created Queue...{name}")

    async def consumeExchange(self, name, callback, queue='', durable=False,
                              auto_delete=True, ack=True):
        async with self.channel_pool.acquire() as channel:
            result = await channel.declare_exchange(name=name,
                                                    durable=durable,
                                                    auto_delete=auto_delete,
                                                    type=ExchangeType.FANOUT
                                                    )
            
            queue_declared = await channel.declare_queue(
                name=queue,
            )
            await queue_declared.bind(result)
            await queue_declared.consume(callback)
            logging.info("started consuming...")

    async def consumeQueue(self, name, callback, ensure=False):
        async with self.channel_pool.acquire() as channel:
            queue = await channel.get_queue(name=name, ensure=ensure)
            await queue.consume(callback)
 
    async def publish_exchange(self, name, message, queue='', ensure=True):
        async with self.channel_pool.acquire() as channel:
            exchange = await channel.get_exchange(name=name, ensure=ensure)
            message = Message(message.encode())
            await exchange.publish(message, routing_key=queue)
    
    async def publish_queue(self, queue, message, ensure=False):
        async with self.channel_pool.acquire() as channel:
            exchange = await channel.get_exchange(name='', ensure=ensure)
            message = Message(message.encode())
            await exchange.publish(message, routing_key=queue)


rabbit_handler = RabbitHandler()