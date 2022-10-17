# @Author: Daniel Gomes
# @Date:   2022-08-16 09:35:51
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-25 14:46:28
from flask_login import login_required, LoginManager, current_user, UserMixin
import requests
from api.settings import AuthConfig as config

loginManager = LoginManager()
current_user = current_user
login_required = login_required


class Tenant(UserMixin):
    def __init__(self, name, group, roles):
        super().__init__()
        self.name=name
        self.group = group
        self.roles=roles

    def is_admin(self):
        return 'ADMIN' in self.roles


@loginManager.user_loader
def user_loader(username):
    return None


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