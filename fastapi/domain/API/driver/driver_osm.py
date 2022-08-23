# @Author: Daniel Gomes
# @Date:   2022-08-17 14:59:56
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-23 11:29:46

from functools import wraps
from osmclient import client
from driver.driver import DomainDriver
import requests
from exceptions.domain import CouldNotAuthenticatetoNFVO


class OSMDriver(DomainDriver):
    def __init__(self, host, username, password, project) -> None:
        self.host = self.parse_host(host)
        self.username = username
        self.password = password
        self.project = project
        self.token = None
        self.osm_client = None

    def parse_host(self, host: str, remove_prefix: bool = False):
        if remove_prefix:
            split_url = host.split('://')
            if len(split_url) > 1:
                parsed_url = split_url[1]
                host = parsed_url
        host = host[:-1] if host[-1] == '/' else host
        return host

    def require_session(remove_prefix: bool = False) -> None:
        def inner(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                if not self.osm_client:
                    self.connect_client(remove_prefix)
                return func(self, *args, **kwargs)
            return wrapper
        return inner

    def connect_client(self, remove_prefix: bool = False):
        host = self.parse_host(self.host, remove_prefix)
        self.osm_client = client.Client(
                        host=host,
                        user=self.username,
                        password=self.password,
                        project=self.project)

    def authenticate(self):
        r = requests.post(
            url=f"{self.host}/osm/admin/v1/tokens",
            data={
                'username': self.username,
                'password': self.password,
                'project_id': self.project
            },
            timeout=5,
            verify=False
        )
        if r.status_code != 200:
            raise CouldNotAuthenticatetoNFVO()

    @require_session(remove_prefix=True)
    def instantiateNSI(self, nsiName, nstName, vimAccount,
                       additionalConf=None):
        self.osm_client.nsi.create(
            nst_name=nstName,
            nsi_name=nsiName,
            account=vimAccount,
            config=additionalConf)
        nsiData = self.osm_client.nsi.get(nsiName)
        return nsiData

    @require_session(remove_prefix=True)
    def sendActionNS(self, nsId, additionalConf=None):

        actionId = self.osm_client.ns.exec_op(nsId, "action",
                                              op_data=additionalConf,
                                              wait=True)
        actionInfo = self.osm_client.ns.get_op(actionId)
        return actionInfo

    @require_session(remove_prefix=True)
    def getNSI(self, nsiId):
        return self.osm_client.nsi.get(nsiId)
