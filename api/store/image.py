from dataclasses import asdict

from dacite import from_dict
from pysondb.db import JsonDatabase

from api.model.image_data import PersistentImage


def dict_to_image_data(img):
    return from_dict(data_class=PersistentImage, data=img)


class ImageJsonDatabase(JsonDatabase):

    def __init__(self) -> None:
        super().__init__('img/registry.json', 'id')

    def add_image(self, image: PersistentImage):
        self.delete_by_identifier(image.identifier)
        self.add(asdict(image))
        return image

    def delete_by_identifier(self, identifier):
        for existing_data in self.getByQuery({'identifier': identifier}):
            self.deleteById(existing_data.get('id'))

    def get_for_os(self, os_identifier: str) -> list[PersistentImage]:
        return list(map(dict_to_image_data, self.getByQuery({'os_identifier': os_identifier})))

    def has_image(self, image: PersistentImage) -> bool:
        return 1 == len(self.getByQuery({'os_identifier': image.os_identifier, 'identifier': image.identifier}))


image_registry = ImageJsonDatabase()
