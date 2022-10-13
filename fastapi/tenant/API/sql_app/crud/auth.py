# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-01 17:34:39
import logging
from sqlalchemy.orm import Session

from exceptions.group import GroupNotFound

# custom imports
from .. import models
from aux import auth
from exceptions.auth import UserCreationFailed, TenantDoesNotExist,\
    TenantInvalidCredentials, InvalidUser, PasswordUpdateFailed
import schemas.auth as AuthSchemas
import schemas.message as MessageSchemas

# Logger
logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)

# ---------------------------------------- #
# -----------------  Auth  --------------- #
# ---------------------------------------- #


def create_group(db: Session, name: str):
    db_group = db.query(models.Group).filter(models.Group.name == name).first()
    if not db_group:
        db_group = models.Group(name=name)
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        logging.info(f"Groupd created : {db_group.as_dict()}")
    logging.info(f"Groupd {db_group.as_dict()} was already created")
    return db_group


def get_group(db: Session, name: str):
    return db.query(models.Group).filter(models.Group.name == name).first()


def get_all_groups(db: Session):
    groups = db.query(models.Group).all()
    return [x.as_dict() for x in groups]


def create_role(db: Session, role: str):
    db_role = db.query(models.Role).filter(models.Role.role == role).first()
    if not db_role:
        db_role = models.Role(role=role)
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        logging.info(f"Role created : {db_role.as_dict()}")
    logging.info(f"Role {db_role.as_dict()} was already created")
    return db_role


def register_tenant(db: Session, tenant_data: AuthSchemas.TenantCreate):
    username = tenant_data.username
    db_tenant = db.query(models.Tenant).filter(
                         models.Tenant.username == username).first()
    if db_tenant:
        logging.info(f"Tenant {username} already exists:{db_tenant.as_dict()}")
        return db_tenant
    hashed_password = auth.get_password_hash(tenant_data.password)
    checkpoint = db.begin_nested()
    try:
        db_group = get_group(db, tenant_data.group)
        if not db_group:
            raise GroupNotFound(tenant_data.group)
        db_tenant = models.Tenant(
            username=username,
            password=hashed_password,
            group=db_group
        )
        db.add(db_tenant)
        db.commit()
        db_tenant_roles = []
        for role in tenant_data.roles:
            # get role id
            db_role = db.query(models.Role).filter(
                models.Role.role == role.upper()).first()
            db_user_role = models.Tenant_Role(
                           user=db_tenant.username, role=db_role.id)
            db_tenant_roles.append(db_user_role)
        db.add_all(db_tenant_roles)
        db.commit()
        db.refresh(db_tenant)

    except Exception as e:
        checkpoint.rollback()
        logging.info(f"Could not create Tenant {username}. Reason: {e}")
        raise UserCreationFailed(username)
    
    logging.info(f"Tenant {username} created with success")
    return db_tenant

def getTenantByUsername(db: Session, username: str):
    return db.query(models.Tenant)\
             .filter(models.Tenant.username == username)\
             .first()

def get_all_tenants_info(db: Session):
    tenants_db = db.query(models.Tenant).all()
    tenants_out = [
        AuthSchemas.Tenant(
            username=x.username,
            group=x.group.name,
            roles=get_user_roles(db, x.username)
        ).dict()
        for x in tenants_db
    ]
    return tenants_out

def authenticate_user(db: Session, username: str, password: str):
    # 1 - check if credentials are correct
    try:
        user = db.query(models.Tenant).filter(
            models.Tenant.username == username).first()
        if not auth.verify_password(password, user.password):
            raise TenantInvalidCredentials(username)
    except Exception:
        raise TenantInvalidCredentials(username)
    return user


def get_user_info(db: Session, username: str):
    try:
        db_tenant = db.query(models.Tenant).filter(
            models.Tenant.username == username).first()
    except Exception:
        raise InvalidUser(username)
    tenant_out = AuthSchemas.Tenant(
                    username=username,
                    group=db_tenant.group.name,
                    roles=get_user_roles(db, username)
    )
    return tenant_out


def get_user_roles(db: Session, username: str):
    # 1 - check if user exists
    user = db.query(models.Tenant).filter(
        models.Tenant.username == username).first()   
    if not user:
        raise TenantDoesNotExist(username)
    # 2 - get roles
    user_roles = db.query(models.Tenant_Role).filter(
        models.Tenant_Role.user == user.username).all()
    if len(user_roles) == 0:
        return set()
    # 3 - roles2str
    user_roles_str = []
    for user_role in user_roles:
        role = db.query(models.Role).filter(
            models.Role.id == user_role.role).first()
        user_roles_str.append(role.role)
    return user_roles_str
    

def update_user_password(db: Session, username: str, new_password: str):    
    try:
        # 1 - get user
        db_user = db.query(models.User).filter(
            models.User.username == username).first()   
        # 2 - hash the password and update the db
        hashed_password = auth.get_password_hash(new_password)
        db_user.hashed_password = hashed_password
        db.commit()
        db.refresh(db_user)
    except Exception:
        logging.info(f"Could not update {username}'s passsword")
        raise PasswordUpdateFailed(username)
    
    logging.info(f"{username}'s password updated with success")
    return db_user


def update_tenant_vs_data(db: Session,
                     tenant: models.Tenant,
                     vsi: MessageSchemas.CreateVsiData):

    vsi_in = models.VSI(
        id=vsi.vsiId
    )
    # if vsi already in the Tenant's Vsis remove it, else add it
    found = False
    for vsi_db in tenant.vsis:
        if vsi_db.id == vsi_in.id:
            logging.info(f"Removing VSI with Id {vsi_db.id} for tenant" \
                         + f" {tenant.username} ..."
            )
            tenant.vsis.remove(vsi_db)
            found = True
            break
    
    if not found:
        logging.info(f"Adding VSI with Id {vsi_in.id} for tenant" \
                         + f" {tenant.username} ..."
        )
        tenant.vsis.append(vsi_in)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant