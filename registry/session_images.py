import json
from dataclasses import asdict
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Callable, Any

from dacite import from_dict, Config
from more_itertools import one
from pysondb.db import JsonDatabase

from api.encoder import DateTimeEncoder
from api.model.session_data import SessionData, TransientSessionData


class OpenSpaceSessionImageJsonDatabase(JsonDatabase):

    def __init__(self) -> None:
        self.file_store = Path('sess/')
        self.file_store.mkdir(exist_ok=True)
        super().__init__(str(self.file_store.joinpath('registry.json')), 'id')

    def _get_dump_function(self) -> Callable[..., Any]:
        return partial(json.dump, cls=DateTimeEncoder)

    def add_session_image(self, session: SessionData):
        self.delete_by_identifier(session.identifier)
        self.add(asdict(session))
        return session

session_images_registry: OpenSpaceSessionImageJsonDatabase = OpenSpaceSessionImageJsonDatabase()
