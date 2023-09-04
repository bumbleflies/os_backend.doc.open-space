from dataclasses import asdict
from pathlib import Path

from dacite import from_dict
from more_itertools import one
from pysondb.db import JsonDatabase

from api.model.image_data import ImageDetails


class ImageDetailsJsonDatabase(JsonDatabase):

    def __init__(self) -> None:
        self.file_store = Path('../../map_front/public/img/')
        self.file_store.mkdir(exist_ok=True)
        super().__init__(str(self.file_store.joinpath('details_registry.json')), 'id')

    def add_details(self, image_details: ImageDetails):
        self.add(asdict(image_details))

    def update_image_details(self, image_details: ImageDetails):
        self.updateByQuery({'image_identifier': image_details.image_identifier}, asdict(image_details))

    def has_image_details(self, image_identifier: str) -> bool:
        return len(self.getByQuery({'image_identifier': image_identifier})) > 0

    def get_by_image_identifier(self, image_identifier: str) -> ImageDetails:
        return from_dict(data_class=ImageDetails, data=one(self.getByQuery({'image_identifier': image_identifier})))

    def delete_by_image_identifier(self, image_identifier: str) -> None:
        found_image = self.getByQuery({'image_identifier': image_identifier})
        if len(found_image) == 1:
            self.deleteById(one(found_image).get(self.id_fieldname))


image_details_registry = ImageDetailsJsonDatabase()
