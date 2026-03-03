from typing import Annotated, Any

import regex
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from keycloak import KeycloakOpenID
from pydantic import BaseModel

from .configuration import settings
from .util.logger import retrieve_logger

_ORGANIZATION_GROUP_REGEX = r"^org-(?<id>[0-9]+)-(?<name>[\p{L}\p{N}\s\-\._&%+#@!(),:;\'\/\?]+)$"

_CLAIMS_TO_CHECK = dict.fromkeys(["iss", "sub", "aud", "exp", "groups"])

_LOGGER = retrieve_logger(__name__)


class AuthenticationOrganization(BaseModel):
    id: str
    name: str


class AuthenticationUser(BaseModel):
    id: str
    username: str
    email: str
    organization: AuthenticationOrganization
    roles: list[str] = []


_keycloak_openid = KeycloakOpenID(
    server_url=settings.keycloak.server_url,
    client_id=settings.keycloak.client_id,
    realm_name=settings.keycloak.realm,
    client_secret_key=settings.keycloak.client_secret_key,
)

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _retrieve_roles(decoded_token: dict[Any, Any]) -> list[str]:

    roles: list[str] = []
    realm_access = decoded_token.get("realm_access")
    if realm_access and "roles" in realm_access:
        roles.extend(realm_access["roles"])

    resource_access = decoded_token.get("resource_access")
    if resource_access and settings.keycloak.client_id in resource_access:
        client_claims = resource_access[settings.keycloak.client_id]
        if isinstance(client_claims, dict):
            client_roles = client_claims.get("roles")
            if client_roles:
                roles.extend(client_roles)

    return roles


def _retrieve_organization(decoded_token: dict[Any, Any]) -> AuthenticationOrganization:

    groups: list[str] = decoded_token.get("groups", [])

    for group in groups:
        match = regex.match(_ORGANIZATION_GROUP_REGEX, group)
        if match:
            organization_id = match.group("id")
            organization_name = match.group("name").strip()

            return AuthenticationOrganization(
                id=organization_id,
                name=organization_name
            )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials: Organization missing in token",
        headers={"WWW-Authenticate": "Bearer"}
    )


def retrieve_authentication_user(
    token: str = Depends(_oauth2_scheme)
) -> AuthenticationUser:

    try:
        decoded_token = _keycloak_openid.decode_token(
            token,
            check_claims=_CLAIMS_TO_CHECK)

        user_id = decoded_token.get("sub")

        if not (user_id or isinstance(user_id, str)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: User ID missing in token",
                headers={"WWW-Authenticate": "Bearer"})

        email = decoded_token.get("email")

        if not (email and isinstance(email, str)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: Email missing in token",
                headers={"WWW-Authenticate": "Bearer"})

        username = (
            decoded_token.get("preferred_username")
            or email)

        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: Preferred username and email missing in token",
                headers={"WWW-Authenticate": "Bearer"})

        roles = _retrieve_roles(decoded_token)

        organization = _retrieve_organization(decoded_token)

        return AuthenticationUser(
            id=user_id,
            username=username,
            email=email,
            organization=organization,
            roles=roles)

    except Exception as exception:
        _LOGGER.warning(f"Token validation error: {exception}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


CurrentUser = Annotated[AuthenticationUser, Depends(retrieve_authentication_user)]
