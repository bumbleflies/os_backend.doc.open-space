import json
from dataclasses import asdict
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Callable, Any, Mapping

from dacite import from_dict, Config
from more_itertools import one
from pysondb.db import JsonDatabase
from pysondb.errors import DataNotFoundError

from api.encoder import DateTimeEncoder
from api.model.os_data import PersistentOpenSpaceData


def dict_to_os_data(os: Mapping[str, Any]):
    return from_dict(data_class=PersistentOpenSpaceData, data=os, config=Config(type_hooks={
        datetime: datetime.fromisoformat
    }))


class OpenSpaceJsonDatabase(JsonDatabase):

    def __init__(self) -> None:
        self.file_store = Path('_registry/')
        self.file_store.mkdir(exist_ok=True)
        super().__init__(str(self.file_store.joinpath('os.json')), 'id')

    def _get_dump_function(self) -> Callable[..., Any]:
        return partial(json.dump, cls=DateTimeEncoder)

    def add_os(self, os: PersistentOpenSpaceData) -> PersistentOpenSpaceData:
        self.delete_by_identifier(os.identifier)
        self.add(asdict(os))
        return os

    def get_all_os(self) -> list[PersistentOpenSpaceData]:
        return list(map(dict_to_os_data, self.getAll()))

    def delete_by_identifier(self, identifier: str) -> None:
        for existing_data in self.getByQuery({'identifier': identifier}):
            self.deleteById(existing_data.get(self.id_fieldname))

    def update_by_identifier(self, identifier: str, new_os: PersistentOpenSpaceData) -> PersistentOpenSpaceData:
        found_images = self.getByQuery({'identifier': identifier})
        if 1 != len(found_images):
            raise DataNotFoundError({'identifier': identifier})
        self.updateById(one(found_images).get(self.id_fieldname), asdict(new_os))
        return new_os


os_registry:OpenSpaceJsonDatabase = OpenSpaceJsonDatabase()
