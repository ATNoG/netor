# @Author: Daniel Gomes
# @Date:   2022-08-16 16:26:28
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-23 11:29:31


import json
from rabbitmq.adaptor import RabbitHandler
import aux.constants as Constants
import schemas.message as MessageSchemas
import sql_app.crud.domain as CRUDDomain
from sql_app.database import SessionLocal
import logging
from exceptions.domain import DomainDriverNotFound, DomainLayersCouldNotBeFound

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

    async def run(self):
        db_gen = get_db()
        db = next(db_gen)
        try:
            domain, domainLayer, driver = CRUDDomain.getDomainInfo(
                db, self.payload.data.domainId)
            if not driver:
                raise DomainDriverNotFound()
            if not domainLayer:
                raise DomainLayersCouldNotBeFound()
            response = MessageSchemas.Message(vsiId=self.payload.vsiId)
            if self.payload.msgType == Constants.TOPIC_INSTANTIATE_NSI:
                nsiData = driver.instantiateNSI(
                        self.payload.data.name,
                        self.payload.data.nstId,
                        domainLayer.vimAccount,
                        self.payload.data.additionalConf)
                nssNsrId = {}
                tunnelServiceId = None
                for nss in nsiData["_admin"]["nsrs-detailed-list"]:
                    if nss["nss-id"] == "interdomain-tunnel-peer":
                        tunnelServiceId = nss["nsrId"]
                    nssNsrId[nss["nss-id"]] = nss["nsrId"]

                data = MessageSchemas.UpdateResourcesNfvoIdsData(
                    componentName=self.payload.data.name,
                    componentId=tunnelServiceId,
                    additionalData=nssNsrId)

                response.msgType = Constants.TOPIC_UPDATE_NFVO_IDS,
                response.message = "Sending Resource's Components Ids",
                response.data = data

            elif self.payload.msgType == Constants.TOPIC_ACTION_NS:
                res = driver.sendActionNS(
                    self.payload.data.nsId,
                    self.payload.data.additionalConf
                )
                data = MessageSchemas.ActionResponseData(
                    primitiveName=self.payload.data.primitiveName,
                    status=res['operationState'],
                    output=res["detailed-status"]["output"]
                )
                response.msgType = Constants.TOPIC_ACTION_RESPONSE
                response.message = "Returning NS action result",
                response.data = data
            elif self.payload.msgType == Constants.TOPIC_FETCH_NSI_INFO:
                nsiInfo = driver.getNSI(
                    self.payload.data.nsiId
                )
                data = MessageSchemas.NsiInfoData(
                    vsiId=self.payload.vsiId,
                    nsiId=self.payload.data.nsiId,
                    nsiInfo=nsiInfo
                )
                response.msgType = Constants.TOPIC_NSI_INFO
                response.message = f"Sending NSI {self.payload.data.nsiId} inf"
                response.data = data
            else:
                return
        except Exception as e:
            error_msg = f"Error performing action {self.payload.msgType}" + \
                        f" in domain {self.payload}: {str(e)}"
            response.msgType = Constants.TOPIC_ERROR
            response.message = error_msg
        response = response.dict()
        logging.info("sent message:" + str(response))
        await self.messaging.publish_exchange(
            Constants.EXCHANGE_MGMT,
            message=json.dumps(response)
        )
        return
