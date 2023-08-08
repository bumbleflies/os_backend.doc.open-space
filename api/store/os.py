import json
from dataclasses import asdict
from datetime import datetime
from functools import partial
from typing import Callable, Any

from dacite import from_dict, Config
from pysondb.db import JsonDatabase

from api.encoder import DateTimeEncoder
from api.model.os_data import PersistentOpenSpaceData


def dict_to_os_data(os):
    return from_dict(data_class=PersistentOpenSpaceData, data=os, config=Config(type_hooks={
        datetime: datetime.fromisoformat
    }))


class OpenSpaceJsonDatabase(JsonDatabase):

    def __init__(self) -> None:
        super().__init__('os/registry.json', 'id')

    def _get_dump_function(self) -> Callable[..., Any]:
        return partial(json.dump, cls=DateTimeEncoder)

    def add_os(self, os: PersistentOpenSpaceData) -> PersistentOpenSpaceData:
        self.delete_by_identifier(os.identifier)
        self.add(asdict(os))
        return os

    def delete_by_identifier(self, identifier: str) -> None:
        for existing_data in self.getByQuery({'identifier': identifier}):
            self.deleteById(existing_data.get('id'))

    def update_by_identifier(self, identifier: str, new_os: PersistentOpenSpaceData) -> PersistentOpenSpaceData:
        self.updateByQuery({'identifier': identifier}, asdict(new_os))
        return new_os


os_registry = OpenSpaceJsonDatabase()
