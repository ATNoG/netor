# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-12 10:24:58

from fastapi.responses import JSONResponse
# custom imports
from datetime import datetime
import json

import logging
import requests
import aux.constants as Constants
# Logger
logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)
def create_response(status_code=200, data=[], errors=[],
                    success=True, message=""):
    return JSONResponse(status_code=status_code,
                        content={"message": message, "success": success,
                                 "data": data, "errors": errors},
                        headers={"Access-Control-Allow-Origin": "*"})

def send_instantiation_ts(vsiId, domain, action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    logging.info(f"Publishing timestamp for action {action}...")
    _json = {
        "action": action,
        "timestamp": timestamp,
        "domain": "XYZ"
    }
    try:
        r = requests.post(
            url=f"http://{Constants.TEST_MANAGER_HOST}:" +
                f"{Constants.TEST_MANAGER_PORT}/timestamp/{vsiId}",
            json=_json
        )
        if r.status_code != 200:
            msg = r.json()['message']
            logging.error(f"Error publishing. Reason: {msg}")
            return msg
        else:
            _ = r.json()
            logging.info(f"Success Publishing result for action {action}")
    except Exception as e:
        logging.error(f"Could not Publish result. Reason: {e}")