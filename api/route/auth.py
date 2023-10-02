import os

from auth0.authentication import GetToken
from dotenv import load_dotenv
from fastapi import APIRouter, Security
from fastapi import Depends
from fastapi_auth0 import Auth0, Auth0User
from fastapi_permissions import Authenticated, configure_permissions, Everyone
from starlette import status
from starlette.responses import Response

from api.model.error import ErrorMessage

load_dotenv()
assert os.getenv('OS_AUTH_DOMAIN')
assert os.getenv('OS_AUTH_AUDIENCE')

auth = Auth0(domain=os.getenv('OS_AUTH_DOMAIN'), api_audience=os.getenv('OS_AUTH_AUDIENCE'))

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


def get_active_principals(user: Auth0User = Depends(auth.get_user)):
    if user:
        # user is logged in
        principals = [Everyone, Authenticated]
        principals.extend(getattr(user, "principals", []))
        principals.append(f'user:{user.id}')
    else:
        # user is not logged in
        principals = [Everyone]
    return principals


Permission = configure_permissions(get_active_principals)


@auth_router.get('', dependencies=[Depends(auth.authcode_scheme)])
def get_auth(user: Auth0User = Security(auth.get_user)):
    return user


@auth_router.get('/token')
def get_access_token(email: str, password: str, response: Response):
    if not (os.getenv('OS_AUTH_TEST_CLIENT_ID') and os.getenv('OS_AUTH_TEST_CLIENT_SECRET')):
        response.status_code = status.HTTP_405_METHOD_NOT_ALLOWED
        return ErrorMessage('Only available during testing')

    get_token = GetToken(os.getenv('OS_AUTH_DOMAIN'), os.getenv('OS_AUTH_TEST_CLIENT_ID'),
                         client_secret=os.getenv('OS_AUTH_TEST_CLIENT_SECRET'))
    token = get_token.login(email, password,
                            realm='Username-Password-Authentication',
                            audience=os.getenv('OS_AUTH_AUDIENCE'))
    return token['access_token']
