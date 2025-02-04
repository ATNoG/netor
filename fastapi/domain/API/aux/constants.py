# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-02 09:41:27


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

COORDINATOR_HOST = None
COORDINATOR_PORT = None


IDP_IP = None
IDP_CLIENTID = None
IDP_ClIENT_SECRET = None
IDP_ADMIN_ClIENTSECRET = None
IDP_REALM = None
IDP_CALLBACK_URI = None

TOPIC_CREATEVSI = "createVSI"
TOPIC_DOMAININFO = "domainInfo"
TOPIC_INSTANTIATE_NSI = "instantiateNsi"
TOPIC_INSTANTIATE_NS = "instantiateNs"
TOPIC_DELETE_NSI = "deleteNSI"
TOPIC_ACTION_NS = "actionNs"
TOPIC_ACTION_NSI = "actionNsi"
TOPIC_FETCH_NS_INFO = "getNsInfo"
TOPIC_FETCH_NSI_INFO = "getNsiInfo"
TOPIC_FETCH_ACTION_INFO = "getPrimitiveInfo"
TOPIC_NSI_INFO = "nsiInfo"
TOPIC_NS_INFO = "nsInfo"

TOPIC_ERROR = "errorOccured"


TOPIC_UPDATE_NFVO_IDS = 'updateResourcesNfvoIds'
TOPIC_ACTION_RESPONSE = 'actionResponse'
EXCHANGE_MGMT = "vsLCM_Management"
QUEUE_DOMAIN = "vsDomain"

DOMAIN_LAYER_TYPES = ['OSM_NSP']

OSM_LAYER_TYPE = 'OSM_NSP'
