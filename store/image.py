from os import listdir
from pathlib import Path

from fastapi import UploadFile

from api.model.image_data import PersistentImage


class ImageStore:
    def __init__(self, path='img'):
        self._image_storage = Path(path)

    async def save(self, image: UploadFile, persistent_image: PersistentImage):
        os_path = self.image_dir(persistent_image)
        if not os_path.exists():
            os_path.mkdir()
        with os_path.joinpath(persistent_image.identifier) as image_file:
            image_file.write_bytes(await image.read())
        return persistent_image

    def load(self, os_identifier: str) -> list[PersistentImage]:
        os_image_path = self.storage_path.joinpath(os_identifier)
        if os_image_path.exists():
            return [PersistentImage(os_identifier, identifier=pi) for pi in listdir(os_image_path)]
        else:
            return []

    def get(self, persistent_image: PersistentImage):
        return self.image_dir(persistent_image).joinpath(persistent_image.identifier)

    def delete(self, persistent_image: PersistentImage):
        if self.get(persistent_image).exists():
            self.get(persistent_image).unlink()
            if len(listdir(self.image_dir(persistent_image))) == 0:
                self.image_dir(persistent_image).rmdir()

    @property
    def storage_path(self):
        if not self._image_storage.exists():
            self._image_storage.mkdir()
        return self._image_storage

    def image_dir(self, persistent_image: PersistentImage):
        return self.storage_path.joinpath(persistent_image.os_identifier)


image_storage = ImageStore()
