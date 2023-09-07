from fastapi import APIRouter
from more_itertools import one
from pysondb.errors import DataNotFoundError
from starlette import status
from starlette.responses import Response

from api.model.error import ErrorMessage
from api.model.os_data import TransientOpenSpaceData, PersistentOpenSpaceData
from api.route.session import delete_session
from registry.os import os_registry, dict_to_os_data
from registry.session import session_registry

os_router = APIRouter(
    prefix='/os',
    tags=['open space']
)


@os_router.post('/', status_code=status.HTTP_201_CREATED)
async def create_os(osd: TransientOpenSpaceData) -> PersistentOpenSpaceData:
    os_persistent = PersistentOpenSpaceData.from_data(osd)
    return os_registry.add_os(os_persistent)


@os_router.get('/')
async def get_open_spaces() -> list[PersistentOpenSpaceData]:
    return os_registry.get_all_os()


@os_router.get('/{identifier}')
def get_open_space(identifier, response: Response) -> PersistentOpenSpaceData | ErrorMessage:
    query_result = os_registry.getByQuery({'identifier': identifier})
    if 1 == len(query_result):
        return dict_to_os_data(one(query_result))
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorMessage('Invalid OpenSpace Identifier')


@os_router.delete('/{identifier}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_open_space(identifier: str):
    os_registry.delete_by_identifier(identifier)
    for session in session_registry.get_all_sessions(identifier):
        session_registry.delete_by_identifier(session.identifier)


@os_router.put('/{identifier}')
async def update_open_space(identifier: str, osd: TransientOpenSpaceData,
                            response: Response) -> PersistentOpenSpaceData | ErrorMessage:
    os_persistent = PersistentOpenSpaceData.from_data(osd)
    os_persistent.identifier = identifier
    try:
        return os_registry.update_by_identifier(identifier, os_persistent)
    except DataNotFoundError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorMessage('Invalid OpenSpace Identifier')
