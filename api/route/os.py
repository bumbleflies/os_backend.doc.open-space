import json
from dataclasses import asdict
from datetime import datetime
from functools import partial
from typing import Callable, Any

from dacite import from_dict, Config
from fastapi import APIRouter
from pysondb.db import JsonDatabase
from pysondb.errors import DataNotFoundError
from starlette import status
from starlette.responses import Response

from api.encoder import DateTimeEncoder
from api.model.os_data import TransientOpenSpaceData, PersistentOpenSpaceData


def dict_to_os_data(os):
    return from_dict(data_class=PersistentOpenSpaceData, data=os, config=Config(type_hooks={
        datetime: datetime.fromisoformat
    }))


class OpenSpaceJsonDatabase(JsonDatabase):

    def __init__(self) -> None:
        super().__init__('os/registry.json', 'id')

    def _get_dump_function(self) -> Callable[..., Any]:
        return partial(json.dump, cls=DateTimeEncoder)

    def delete_by_identifier(self, identifier):
        for existing_data in self.getByQuery({'identifier': identifier}):
            self.deleteById(existing_data.get('id'))

    def update_by_identifier(self, identifier, new_os: PersistentOpenSpaceData) -> PersistentOpenSpaceData:
        self.updateByQuery({'identifier': identifier}, asdict(new_os))
        return new_os


os_router = APIRouter(
    prefix='/os',
    tags=['open space']
)

os_storage = OpenSpaceJsonDatabase()


@os_router.post('/', status_code=status.HTTP_201_CREATED)
async def create_os(osd: TransientOpenSpaceData) -> PersistentOpenSpaceData:
    os_persistent = PersistentOpenSpaceData.from_data(osd)
    os_storage.delete_by_identifier(os_persistent.identifier)
    os_storage.add(asdict(os_persistent))
    return os_persistent


@os_router.get('/')
async def get_open_spaces() -> list[PersistentOpenSpaceData]:
    return list(map(dict_to_os_data, os_storage.getAll()))


@os_router.get('/{identifier}')
def get_open_space(identifier, response: Response):
    query_result = os_storage.getByQuery({'identifier': identifier})
    if 1 == len(query_result):
        return dict_to_os_data(query_result[0])
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'message': 'Invalid OpenSpace Identifier'}


@os_router.delete('/{identifier}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_open_space(identifier: str):
    os_storage.delete_by_identifier(identifier)


@os_router.put('/{identifier}')
async def update_open_space(identifier: str, osd: TransientOpenSpaceData, response: Response):
    os_persistent = PersistentOpenSpaceData.from_data(osd)
    os_persistent.identifier = identifier
    try:
        return os_storage.update_by_identifier(identifier, os_persistent)
    except DataNotFoundError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'message': 'Invalid OpenSpace Identifier'}
