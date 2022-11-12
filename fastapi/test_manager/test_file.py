# @Author: Daniel Gomes
# @Date:   2022-11-12 10:29:52
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-12 13:54:40
import requests
import logging
from datetime import datetime
# Logger
logger = logging.getLogger(__name__)


class ResultsPublishingWrapper:
    def __init__(self, ip, vsi_id) -> None:
        self.ip = ip
        self.vsi_id = vsi_id
        self.url = f"{self.ip}/timestamp"

    def publish_data(self, domain, action):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(timestamp)
        logger.info(f"Publishing timestamp for action {action}...")
        _json = {
            "action": action,
            "timestamp": timestamp,
            "domain": domain
        }
        try:
            r = requests.post(
                url=f"{self.url}/{self.vsi_id}",
                json=_json
            )
            if r.status_code != 200:
                msg = r.json()['message']
                logging.error(f"Error publishing. Reason: {r.__dict__}")
            else:
                _ = r.json()
                logging.info(f"Success Publishing result for action {action}")
        except Exception as e:
            logging.error(f"Could not Publish result. Reason: {e}")


if __name__ == "__main__":
    wrapper = ResultsPublishingWrapper(
        ip="http://localhost:8000",
        vsi_id="1"
    )
    wrapper.publish_data(domain=None, action="REQUEST_TS")
    wrapper.publish_data(domain="ITAV", action="INSTANTIATE_VSI_TS")
    wrapper.publish_data(domain="ITAV", action="DNS_SD_REGISTER_TS")

