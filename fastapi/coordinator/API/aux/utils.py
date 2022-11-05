# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-05 18:04:05


from fastapi.responses import JSONResponse
from exceptions.auth import CouldNotConnectToTenant, CouldNotConnectToDomain
import requests
from sqlalchemy.orm import Session
import aux.constants as Constants
from fastapi.encoders import jsonable_encoder
from cryptography.fernet import Fernet
import json
from schemas import vertical as VerticalSchemas

def create_response(status_code=200, data=[], errors=[],
                    success=True, message=""):
    return JSONResponse(status_code=status_code,
                        content={"message": message, "success": success,
                                 "data": data, "errors": errors},
                        headers={"Access-Control-Allow-Origin": "*"})


def check_admin_role(user):
    return Constants.IDP_ADMIN_USER in user.roles


def get_tenant_info(token):
    url = f"http://{Constants.TENANT_HOST}:{Constants.TENANT_PORT}"\
          + "/oauth/validate"
    try:
        r = requests.get(
            url=url,
            headers={'Authorization': f'Bearer {token}'},
            timeout=5,
            verify=False
        )
        print(r)
        if r.status_code != 200:
            raise CouldNotConnectToTenant()
        data = r.json()
        
        return data
    except Exception as e:
        print(e)
        raise CouldNotConnectToTenant()


def get_domain_info(token, domain_id):
    url = f"http://{Constants.DOMAIN_HOST}:{Constants.DOMAIN_PORT}"\
          + f"/domain/{domain_id}"
    try:
        r = requests.get(
            url=url,
            headers={'Authorization': f'Bearer {token}'},
            timeout=5,
            verify=False
        )
        data = r.json()
        return data['data']
    except Exception:
        raise CouldNotConnectToDomain()


def get_catalogue_vsd_info(token, vsd_id):
    url = f"http://{Constants.CATALOGUE_HOST}:{Constants.CATALOGUE_PORT}"\
          + f"/vsdescriptor?vsd_id={vsd_id}"
    try:
        r = requests.get(
            url=url,
            headers={'Authorization': f'Bearer {token}'},
            timeout=5,
            verify=False
        )
        data = r.json()
        return data['data']
    except Exception:
        raise CouldNotConnectToDomain()


def update_db_object(db: Session, db_obj: object, obj_in: dict,
                     add_to_db: bool = True):
    obj_data = jsonable_encoder(db_obj)
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    if add_to_db:
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    return db_obj


def parse_dns_params_to_vnf(vsiId: int, vs_in: VerticalSchemas.VSICreate):
    key = Fernet.generate_key()
    dns_params = {
            "dns_ip": Constants.DNS_IP,
            "dns_port": Constants.DNS_PORT,
            "dns_api_port": Constants.DNS_API_PORT,
            "dns_api_key": Constants.DNS_API_KEY,
            "dns_encryption_key": str(key.decode()),
            "dns_zone": f"vsi-{vsiId}.netor.",
            "vsi_id": str(vsiId)
        }
    for peer in vs_in.additionalConf:
        peer_conf = peer.conf
        vnf_params = peer_conf['netslice-subnet'][0]['additionalParamsForVnf']
        for vnf in vnf_params:
            for param in dns_params:
                vnf['additionalParams'][param] = dns_params[param]
        peer.conf = json.dumps(peer_conf)
    return vs_in
