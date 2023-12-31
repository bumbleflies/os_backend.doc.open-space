import json
from dataclasses import asdict
from functools import partial
from pathlib import Path
from typing import Callable, Any

from more_itertools import one
from pysondb.db import JsonDatabase
from pysondb.errors import DataNotFoundError

from api.encoder import DateTimeEncoder
from api.model.os_data import PersistentOpenSpaceData, dict_to_os_data, PersistentOpenSpaceDataWithHeader, \
    TransientOpenSpaceData
from registry.image import image_registry


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

    def update_by_identifier(self, identifier: str, new_os: TransientOpenSpaceData) -> PersistentOpenSpaceData:
        found_os = self.getByQuery({'identifier': identifier})
        if 1 != len(found_os):
            raise DataNotFoundError({'identifier': identifier})
        self.updateById(one(found_os).get(self.id_fieldname), asdict(new_os))
        return self.get_os(identifier)

    def get_os(self, identifier: str, with_header_images: bool = False):
        query_result = self.getByQuery({'identifier': identifier})
        os = None
        if 1 == len(query_result):
            os = dict_to_os_data(one(query_result))
            if with_header_images:
                os = PersistentOpenSpaceDataWithHeader.from_os_header(os, image_registry.get_for_os(os.identifier,
                                                                                                    with_header_images))
        return os


os_registry: OpenSpaceJsonDatabase = OpenSpaceJsonDatabase()
