# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-12 13:58:02


SECRET_KEY = "99cb3e97787cf81a7f418c42b96a06f77ce25ddbb2f7f83a53cf3474896624f9"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
DEFAULT_ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin"
}
IDP_ADMIN_USER = "NetOr-Admin"
IDP_TENANT_USER = "NetOr-Tenant"
DB_NAME = None
DB_LOCATION = None
DB_USER = None
DB_PASSWORD = None

RABBITMQ_USER = None
RABBITMQ_PASS = None
RABBITMQ_IP = None
RABBITMQ_PORT = None


IDP_IP = None
IDP_CLIENTID = None
IDP_ClIENT_SECRET = None
IDP_ADMIN_ClIENTSECRET = None
IDP_REALM = None
IDP_CALLBACK_URI = None

DOMAIN_HOST = None
DOMAIN_PORT = None

CATALOGUE_HOST = None
CATALOGUE_PORT = None


TEST_MANAGER_HOST = None
TEST_MANAGER_PORT = None

DNS_IP = None
DNS_PORT = None
DNS_API_KEY = None
DNS_API_PORT = None
DNS_NETOR_IP = None
DNS_PEER_IP = None
TOPIC_CREATEVSI = "createVSI"
TOPIC_REMOVEVSI = "removeVSI"
TOPIC_DOMAININFO = "domainInfo"
TOPIC_INSTANTIATE_NSI = "instantiateNsi"
TOPIC_DELETE_NSI = "deleteNSI"
TOPIC_ACTION_NS = "actionNs"
TOPIC_ACTION_NSI = "actionNsi"
TOPIC_FETCH_NS_INFO = "getNsInfo"
TOPIC_FETCH_NSI_INFO = "getNsiInfo"
TOPIC_NSI_INFO = "nsiInfo"
TOPIC_ERROR = "errorOccured"
TOPIC_VSI_STATUS = "statusUpdate"
TOPIC_PRIMITIVE = "primitive"
TOPIC_ACTION_STATUS = "actionUpdate"

TOPIC_UPDATE_NFVO_IDS = 'updateResourcesNfvoIds'
TOPIC_ACTION_RESPONSE = 'actionResponse'
EXCHANGE_MGMT = "vsLCM_Management"
QUEUE_COORDINATOR = "vsCoordinator"

CREATING_STATUS = "creating"
FAILING_STATUS = "fail"
TERMINATED_STATUS = "terminated"

VSI_REQUEST_TS = "REQUEST_TS"