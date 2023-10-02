from fastapi import APIRouter, Depends
from fastapi_auth0 import Auth0User
from pysondb.errors import DataNotFoundError
from starlette import status
from starlette.responses import Response

from api.model.error import ErrorMessage
from api.model.os_data import TransientOpenSpaceData, PersistentOpenSpaceData, PersistentOpenSpaceDataWithHeader
from api.route.auth import auth, Permission
from registry.os import os_registry
from registry.session import session_registry

os_router = APIRouter(
    prefix='/os',
    tags=['open space']
)


def get_os(identifier: str):
    return os_registry.get_os(identifier)


@os_router.post('/', status_code=status.HTTP_201_CREATED, response_model_exclude_none=True,
                dependencies=[Depends(auth.authcode_scheme)])
async def create_os(osd: TransientOpenSpaceData, user: Auth0User = Depends(auth.get_user)) -> PersistentOpenSpaceData:
    os_persistent = PersistentOpenSpaceData.from_data(osd, user.id)
    return os_registry.add_os(os_persistent)


@os_router.get('/', response_model_exclude_none=True, response_model_exclude_unset=True)
async def get_open_spaces() -> list[PersistentOpenSpaceData]:
    return os_registry.get_all_os()


@os_router.get('/{identifier}', response_model_exclude_none=True)
def get_open_space(identifier: str, with_header_images: bool = False,
                   response: Response = None) -> (PersistentOpenSpaceData |
                                                  PersistentOpenSpaceDataWithHeader |
                                                  ErrorMessage):
    os = os_registry.get_os(identifier, with_header_images)
    if not os:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorMessage('Invalid OpenSpace Identifier')
    return os


@os_router.delete('/{identifier}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(auth.authcode_scheme)])
async def delete_open_space(os=Permission('delete', get_os)):
    os_registry.delete_by_identifier(os.identifier)
    for session in session_registry.get_all_sessions(os.identifier):
        session_registry.delete_by_identifier(session.identifier)


@os_router.put('/{identifier}', response_model_exclude_none=True)
async def update_open_space(osd: TransientOpenSpaceData, os=Permission('update', get_os),
                            response: Response = None) -> PersistentOpenSpaceData | ErrorMessage:
    try:
        return os_registry.update_by_identifier(os.identifier, osd)
    except DataNotFoundError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorMessage('Invalid OpenSpace Identifier')
