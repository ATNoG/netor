# @Author: Daniel Gomes
# @Date:   2022-08-16 16:26:28
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-12 10:24:03


import json
from time import sleep
from rabbitmq.adaptor import RabbitHandler
import aux.constants as Constants
import schemas.message as MessageSchemas
import sql_app.crud.domain as CRUDDomain
from sql_app.database import SessionLocal
import logging
from exceptions.domain import DomainDriverNotFound, DomainLayersCouldNotBeFound
import aux.utils as Utils

# Logger
logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DomainActionHandler:
    def __init__(self, payload: MessageSchemas.Message,
                 messaging: RabbitHandler):
        self.payload = payload
        self.messaging = messaging

    async def start(self):
        await self.startConsuming()

    async def startConsuming(self):
        db_gen = get_db()
        db = next(db_gen)
        try:
            response = MessageSchemas.Message(vsiId=self.payload.vsiId)
            domainId = self.payload.data.domainId
            domain, domainLayer, driver = CRUDDomain.getDomainInfo(
                db, domainId)
            if not driver:
                raise DomainDriverNotFound()
            if not domainLayer:
                raise DomainLayersCouldNotBeFound()
            if self.payload.msgType == Constants.TOPIC_INSTANTIATE_NSI:
                nsiData = driver.instantiateNSI(
                        self.payload.data.name,
                        self.payload.data.nstId,
                        domainLayer.vimAccount,
                        self.payload.data.additionalConf)
                logging.info(f"nsiDATA--->>>{nsiData}")
                nssNsrId = {}
                tunnelServiceId = None
                for nss in nsiData["_admin"]["nsrs-detailed-list"]:
                    if nss["nss-id"] == "tunnel-as-a-service-sd-tunnel-peer":
                        tunnelServiceId = nss["nsrId"]
                    nssNsrId[nss["nss-id"]] = nss["nsrId"]

                data = MessageSchemas.UpdateResourcesNfvoIdsData(
                    componentName=self.payload.data.name,
                    componentId=tunnelServiceId,
                    additionalData=nssNsrId)
                response.msgType = Constants.TOPIC_UPDATE_NFVO_IDS
                response.message = "Sending Resource's Components Ids"
                response.data = data

            elif self.payload.msgType == Constants.TOPIC_ACTION_NS:
                res = driver.sendActionNS(
                    self.payload.data.nsId,
                    self.payload.data.additionalConf
                )
                output = res['detailed-status']
                if type(output) == dict:
                    output = json.dumps(output)
                data = MessageSchemas.ActionResponseData(
                    primitiveName=self.payload.data.primitiveName,
                    actionId=self.payload.data.actionId,
                    nfvoId=res['id'],
                    status=res['operationState'],
                    output=output
                )
                response.msgType = Constants.TOPIC_ACTION_RESPONSE
                response.message = "Returning NS action result"
                response.data = data
            elif self.payload.msgType == Constants.TOPIC_FETCH_NSI_INFO:
                nsiInfo = driver.getNSI(
                    self.payload.data.nsiId
                )
                if type(nsiInfo) == dict:
                    nsiInfo = json.dumps(nsiInfo)
                data = MessageSchemas.NsiInfoData(
                    vsiId=self.payload.vsiId,
                    nsiId=self.payload.data.nsiId,
                    nsiInfo=nsiInfo
                )
                response.msgType = Constants.TOPIC_NSI_INFO
                response.message = f"Sending NSI {self.payload.data.nsiId} inf"
                response.data = data
            elif self.payload.msgType == Constants.TOPIC_DELETE_NSI:
                driver.terminateNSI(self.payload.data.nsiId)
            elif self.payload.msgType == Constants.TOPIC_FETCH_ACTION_INFO:
                res = driver.get_primitive_state(self.payload.data.nfvoId)
                output = res['detailed-status']
                if type(output) == dict:
                    output = json.dumps(output)
                data = MessageSchemas.ActionResponseData(
                    actionId=self.payload.data.actionId,
                    nfvoId=res['id'],
                    status=res['operationState'],
                    output=output
                )
                response.msgType = Constants.TOPIC_ACTION_RESPONSE
                response.message = f"Sending Operation {res['id']} execution state"
                response.data = data
            else:
                return
        except Exception as e:
            error_msg = f"Error performing action {self.payload.msgType}" + \
                        f" in domain: {str(e)}"
            response.msgType = Constants.TOPIC_ERROR
            response.message = error_msg
            response.error = True
        response = response.dict()
        logging.info("sent message:" + str(response))

        await self.messaging.publish_exchange(
            Constants.EXCHANGE_MGMT,
            message=json.dumps(response)
        )