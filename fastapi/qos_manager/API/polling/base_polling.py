
from abc import ABC, abstractmethod
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)

class BasePolling(ABC):
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
    
    def get_running_tasks(self, vsiId):
        pass
    
    def is_job_already_running(self, vsiId):
        vsiId = str(vsiId)
        vsis_running = self.scheduler.get_jobs('default')
        return any([vsi.id == vsiId for vsi in vsis_running])
    
    def my_listener(self, event):
        if e := event.exception:
            logging.warn(f"CSMF Polling for VSI {event.job_id} failed."
                         + f"Reason: {e}")
        else:
            print('The job worked :)')
    
    def start_vsi_polling(self, vsiId):
        pass

    def stop_vsi_polling(self, vsiId):
        pass

    @abstractmethod
    def update_primitive_data(self, vsiId, data):
        pass
    async def poll_vsi_primitive_status(
            self,
            vsiId: int,
            data
    ):
        pass