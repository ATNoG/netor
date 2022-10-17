# @Author: Daniel Gomes
# @Date:   2022-09-26 17:27:03
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-26 18:18:24

from functools import wraps
import pickle
from handler import redis_handler
import logging


logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)

def cache(expire_minutes: int = 60) -> None:

    def decorator(func):
        def setup_args(_kwargs: dict) -> dict:
            """
            Pops from the kwargs of the function,
            a db session object
            """
            copy_kwargs = dict(_kwargs)
            if 'db' in copy_kwargs:
                copy_kwargs.pop('db', None)
            return copy_kwargs

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            data = await redis_handler.get_hash_value()
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
