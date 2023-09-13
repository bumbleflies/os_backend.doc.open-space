from dataclasses import asdict
from pathlib import Path
from typing import Any

from dacite import from_dict
from pysondb.db import JsonDatabase

from api.model.image_data import SessionImage, HeaderData
from registry.image import header_filter, any_filter


def dict_to_session_image(img):
    return from_dict(data_class=SessionImage, data=img)


class OpenSpaceSessionImageJsonDatabase(JsonDatabase):

    def __init__(self) -> None:
        self.file_store = Path('_registry/')
        self.file_store.mkdir(exist_ok=True)
        super().__init__(str(self.file_store.joinpath('session_images.json')), 'id')

    def add_session_image(self, session_image: SessionImage) -> SessionImage:
        self.add(asdict(session_image))
        return session_image

    def get_for_session(self, os_identifier: str, session_identifier: str, only_header: bool = False) \
            -> list[SessionImage]:
        used_filter = only_header and header_filter or any_filter
        return list(filter(used_filter, map(dict_to_session_image,
                                            self.getByQuery({'os_identifier': os_identifier,
                                                             'session_identifier': session_identifier}))))

    def query_image(self, session_image: SessionImage) -> list[dict[str, Any]]:
        return self.getByQuery({'os_identifier': session_image.os_identifier,
                                'session_identifier': session_image.session_identifier,
                                'identifier': session_image.identifier})

    def has_image(self, session_image: SessionImage) -> bool:
        return len(self.query_image(session_image)) > 0

    def delete(self, session_image: SessionImage) -> None:
        for image in self.query_image(session_image):
            self.deleteById(image.get(self.id_fieldname))

    def update_header(self, session_image: SessionImage, header_data: HeaderData):
        for image in self.query_image(session_image):
            self.updateById(image.get(self.id_fieldname), asdict(header_data))


session_images_registry: OpenSpaceSessionImageJsonDatabase = OpenSpaceSessionImageJsonDatabase()
