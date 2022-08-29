# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-27 11:51:48


SECRET_KEY = "99cb3e97787cf81a7f418c42b96a06f77ce25ddbb2f7f83a53cf3474896624f9"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
DEFAULT_ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin"
}
USER_ROLES = ["ADMIN", "TENANT"]

DB_NAME = None
DB_LOCATION = None
DB_USER = None
DB_PASSWORD = None

RABBITMQ_USER = None
RABBITMQ_PASS = None
RABBITMQ_IP = None
RABBITMQ_PORT = None


TOPIC_CREATEVSI = "createVSI"
TOPIC_ERROR = "errorOccured"

EXCHANGE_MGMT = "vsLCM_Management"