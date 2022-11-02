# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 22:45:02
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-31 11:24:55

# general imports
from fastapi_keycloak.model import OIDCUser
from fastapi.security import OAuth2PasswordBearer
from aux.constants import IDP_ADMIN_USER, IDP_TENANT_USER
from fastapi import (
    HTTPException,
    status
)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls)\
                .__call__(*args, **kwargs)
        return cls._instances[cls]


class MockOIDCUser(metaclass=Singleton):
    mocked_oidc_user = OIDCUser(
        sub="",
        iat=0,
        exp=0,
        email_verified=True,
        preferred_username="",
        realm_access={
            "roles": []
        },
    )

    def get_mocked_oidc_user(self):
        return self.mocked_oidc_user

    def inject_mocked_oidc_user(self, id, username, roles):
        self.mocked_oidc_user = OIDCUser(
            sub=id,
            iat=0,
            exp=0,
            email_verified=True,
            preferred_username=username,
            realm_access={
                "roles": roles
            },
        )


class MockFastAPIKeycloak(metaclass=Singleton):

    def user_auth_scheme(self):
        return OAuth2PasswordBearer(tokenUrl="token_uri")

    def get_current_user(required_roles=None):

        def current_user():
            mocked_oidc_user = MockOIDCUser().get_mocked_oidc_user()
            if required_roles:
                for role in required_roles:
                    if role not in mocked_oidc_user.roles:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Role "{role}" is required to ' +
                            'perform this action',
                        )
            return mocked_oidc_user

        return current_user


def setup_test_idp(monkeypatch, mocker):
    # mock IDP needed environment variables
    monkeypatch.setenv("IDP_SERVER_URL", "test_defined_env")
    monkeypatch.setenv("IDP_CLIENT_ID", "test_defined_env")
    monkeypatch.setenv("IDP_CLIENT_SECRET", "test_defined_env")
    monkeypatch.setenv("IDP_ADMIN_CLIENT_SECRET", "test_defined_env")
    monkeypatch.setenv("IDP_REALM", "test_defined_env")
    monkeypatch.setenv("IDP_CALLBACK_URI", "test_defined_env")
    # mock IDP initialization
    FastAPIKeycloak_mock = mocker.patch("fastapi_keycloak.FastAPIKeycloak")
    FastAPIKeycloak_mock.return_value = MockFastAPIKeycloak


def inject_admin_user():
    # Prepare Mocked OIDC User
    MockOIDCUser().inject_mocked_oidc_user(
        id="0000-0000-0000-0000",
        username="admin",
        roles=[IDP_ADMIN_USER, IDP_TENANT_USER]
    )
