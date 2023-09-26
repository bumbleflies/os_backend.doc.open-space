import os

from dotenv import load_dotenv
from fastapi import APIRouter, Security
from fastapi import Depends
from fastapi_auth0 import Auth0, Auth0User

load_dotenv()
assert os.getenv('OS_AUTH_DOMAIN')
assert os.getenv('OS_AUTH_AUDIENCE')

auth = Auth0(domain=os.getenv('OS_AUTH_DOMAIN'), api_audience=os.getenv('OS_AUTH_AUDIENCE'),
             scopes={'create:os': ''})

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@auth_router.get('', dependencies=[Depends(auth.implicit_scheme)])
def get_auth(user: Auth0User = Security(auth.get_user)):
    return user
