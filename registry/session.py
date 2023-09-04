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
        self.add(asdict(session))
        return session


session_registry = OpenSpaceSessionJsonDatabase()
