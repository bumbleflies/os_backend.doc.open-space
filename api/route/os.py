from fastapi import APIRouter
from more_itertools import one
from pysondb.errors import DataNotFoundError
from starlette import status
from starlette.responses import Response

from api.model.error import ErrorMessage
from api.model.os_data import TransientOpenSpaceData, PersistentOpenSpaceData, PersistentOpenSpaceDataWithHeader, \
    dict_to_os_data
from registry.image import image_registry
from registry.os import os_registry
from registry.session import session_registry

os_router = APIRouter(
    prefix='/os',
    tags=['open space']
)


@os_router.post('/', status_code=status.HTTP_201_CREATED, response_model_exclude_none=True)
async def create_os(osd: TransientOpenSpaceData) -> PersistentOpenSpaceData:
    os_persistent = PersistentOpenSpaceData.from_data(osd)
    return os_registry.add_os(os_persistent)


@os_router.get('/', response_model_exclude_none=True)
async def get_open_spaces() -> list[PersistentOpenSpaceData]:
    return os_registry.get_all_os()


@os_router.get('/{identifier}', response_model_exclude_none=True)
def get_open_space(identifier: str, with_header_images: bool = False,
                   response: Response = None) -> (PersistentOpenSpaceData |
                                                  PersistentOpenSpaceDataWithHeader |
                                                  ErrorMessage):
    query_result = os_registry.getByQuery({'identifier': identifier})
    if 1 == len(query_result):
        os = dict_to_os_data(one(query_result))
        if with_header_images:
            os = PersistentOpenSpaceDataWithHeader.from_os_header(os, image_registry.get_for_os(os.identifier,
                                                                                                with_header_images))
        return os
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorMessage('Invalid OpenSpace Identifier')


@os_router.delete('/{identifier}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_open_space(identifier: str):
    os_registry.delete_by_identifier(identifier)
    for session in session_registry.get_all_sessions(identifier):
        session_registry.delete_by_identifier(session.identifier)


@os_router.put('/{identifier}', response_model_exclude_none=True)
async def update_open_space(identifier: str, osd: TransientOpenSpaceData,
                            response: Response) -> PersistentOpenSpaceData | ErrorMessage:
    os_persistent = PersistentOpenSpaceData.from_data(osd)
    os_persistent.identifier = identifier
    try:
        return os_registry.update_by_identifier(identifier, os_persistent)
    except DataNotFoundError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorMessage('Invalid OpenSpace Identifier')
