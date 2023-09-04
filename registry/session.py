import json
from dataclasses import asdict
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Callable, Any

from dacite import from_dict, Config
from pysondb.db import JsonDatabase

from api.encoder import DateTimeEncoder
from api.model.session_data import SessionData


def dict_to_session(session_dict):
    return from_dict(data_class=SessionData, data=session_dict, config=Config(type_hooks={
        datetime: datetime.fromisoformat
    }))


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

    def get_all_sessions(self, os_identifier: str):
        return list(map(dict_to_session, self.getByQuery({'os_identifier': os_identifier})))


session_registry: OpenSpaceSessionJsonDatabase = OpenSpaceSessionJsonDatabase()
