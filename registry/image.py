from dataclasses import asdict
from pathlib import Path
from typing import Any

from dacite import from_dict
from more_itertools import one
from pysondb.db import JsonDatabase

from api.model.image_data import PersistentImage


def dict_to_image_data(img):
    return from_dict(data_class=PersistentImage, data=img)

class ImageJsonDatabase(JsonDatabase):

    def __init__(self) -> None:
        self.file_store = Path('img/')
        self.file_store.mkdir(exist_ok=True)
        super().__init__(str(self.file_store.joinpath('registry.json')), 'id')

    def add_image(self, image: PersistentImage) -> PersistentImage:
        self.delete_by_identifier(image.identifier)
        self.add(asdict(image))
        return image

    def delete_by_identifier(self, identifier: str):
        for existing_data in self.getByQuery({'identifier': identifier}):
            self.deleteById(existing_data.get(self.id_fieldname))

    def get_for_os(self, os_identifier: str) -> list[PersistentImage]:
        return list(map(dict_to_image_data, self.getByQuery({'os_identifier': os_identifier})))

    def has_image(self, image: PersistentImage) -> bool:
        return 1 == len(self.query_image(image))

    def get_image(self, image: PersistentImage) -> dict[str, Any]:
        return one(self.query_image(image))

    def query_image(self, image: PersistentImage) -> list[dict[str, Any]]:
        return self.getByQuery({'os_identifier': image.os_identifier, 'identifier': image.identifier})


image_registry = ImageJsonDatabase()
