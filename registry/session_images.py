import json
from dataclasses import asdict
from functools import partial
from pathlib import Path
from typing import Callable, Any

from dacite import from_dict
from pysondb.db import JsonDatabase

from api.encoder import DateTimeEncoder
from api.model.image_data import SessionImage


def dict_to_session_image(img):
    return from_dict(data_class=SessionImage, data=img)


class OpenSpaceSessionImageJsonDatabase(JsonDatabase):

    def __init__(self) -> None:
        self.file_store = Path('_registry/')
        self.file_store.mkdir(exist_ok=True)
        super().__init__(str(self.file_store.joinpath('session_images.json')), 'id')

    def _get_dump_function(self) -> Callable[..., Any]:
        return partial(json.dump, cls=DateTimeEncoder)

    def add_session_image(self, session_image: SessionImage) -> SessionImage:
        self.add(asdict(session_image))
        return session_image

    def get_for_session(self, os_identifier: str, session_identifier: str) -> list[SessionImage]:
        return list(map(dict_to_session_image, self.getByQuery({'os_identifier': os_identifier,
                                                                'session_identifier': session_identifier})))

    def query_image(self, session_image: SessionImage):
        return self.getByQuery({'os_identifier': session_image.os_identifier,
                                'session_identifier': session_image.session_identifier,
                                'identifier': session_image.identifier})

    def has_image(self, session_image: SessionImage):
        return len(self.query_image(session_image)) > 0


session_images_registry: OpenSpaceSessionImageJsonDatabase = OpenSpaceSessionImageJsonDatabase()
