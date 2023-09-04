import json
from dataclasses import asdict
from functools import partial
from pathlib import Path
from typing import Callable, Any

from pysondb.db import JsonDatabase

from api.encoder import DateTimeEncoder
from api.model.session_data import SessionData


class OpenSpaceSessionJsonDatabase(JsonDatabase):

    def __init__(self) -> None:
        self.file_store = Path('sess/')
        self.file_store.mkdir(exist_ok=True)
        super().__init__(str(self.file_store.joinpath('registry.json')), 'id')

    def _get_dump_function(self) -> Callable[..., Any]:
        return partial(json.dump, cls=DateTimeEncoder)

    def add_session(self, session: SessionData):
        self.delete_by_identifier(session.identifier)
        self.add(asdict(session))
        return session

    def delete_by_identifier(self, identifier: str) -> None:
        for existing_data in self.getByQuery({'identifier': identifier}):
            self.deleteById(existing_data.get(self.id_fieldname))


session_registry = OpenSpaceSessionJsonDatabase()
