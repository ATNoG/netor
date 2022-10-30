# @Author: Daniel Gomes
# @Date:   2022-08-16 09:35:51
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-29 21:45:23
from flask_login import login_required, LoginManager, current_user, UserMixin
import requests
from api.settings import AuthConfig as config

oidc = None
loginManager = LoginManager()
current_user = current_user
login_required = login_required


class Tenant(UserMixin):
    def __init__(self, name, id, roles):
        super().__init__()
        self.name=name
        self.id = id
        self.roles=roles

    def is_admin(self):
        return 'NetOr-Admin' in self.roles


@loginManager.user_loader
def user_loader(username):
    return None


def parse_token_data(payload):
    print(payload.__dict__)
    roles = payload.oidc_token_info['realm_access']['roles']
    _id = payload.oidc_token_info['sub']
    username = payload.oidc_token_info['username']  
    return Tenant(username, _id, roles)

@loginManager.request_loader
def request_loader(request):
    user = None
    if "Authorization" in request.headers:
        token = request.headers.get('Authorization')
        url = f"http://{config.IDP_IP}:{config.IDP_PORT}{config.IDP_ENDPOINT}"
        response = requests.get(url, headers={"Authorization": token})

        if response.status_code==200:
            data=response.json()
            user=Tenant(data["data"]['user_info']["username"],
                        data['data']['user_info']['group'],
                        data["data"]['user_info']["roles"])
    return user