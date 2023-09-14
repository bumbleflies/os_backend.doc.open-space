import asyncio
from asyncio import Task
from os import listdir
from pathlib import Path

from PIL import Image
from fastapi import UploadFile

from api.model.image_data import PersistentImage

THUMBNAIL_SIZE = (150, 150)


class ImageStore:
    def __init__(self, path='img'):
        self._image_storage = Path(path)

    async def save(self, image: UploadFile, persistent_image: PersistentImage) -> (PersistentImage, Task[None]):
        os_path = self.image_dir(persistent_image)
        if not os_path.exists():
            os_path.mkdir()
        with os_path.joinpath(persistent_image.name) as image_file:
            image_file.write_bytes(await image.read())

        return persistent_image, asyncio.create_task(self.create_thumbnail(persistent_image))

    def get(self, persistent_image: PersistentImage):
        return self.image_dir(persistent_image).joinpath(persistent_image.name)

    def get_thumb(self, persistent_image: PersistentImage):
        return self.image_dir(persistent_image).joinpath(persistent_image.thumb_name)

    def delete(self, persistent_image: PersistentImage):
        if self.get(persistent_image).exists():
            self.get(persistent_image).unlink()
            self.get_thumb(persistent_image).unlink()
            if len(listdir(self.image_dir(persistent_image))) == 0:
                self.image_dir(persistent_image).rmdir()

    def delete_all(self):
        for image_dir in listdir(self.storage_path):
            for image_file in listdir(self.storage_path.joinpath(image_dir)):
                self.storage_path.joinpath(image_dir, image_file).unlink()
            self.storage_path.joinpath(image_dir).rmdir()

    @property
    def storage_path(self):
        if not self._image_storage.exists():
            self._image_storage.mkdir()
        return self._image_storage

    def image_dir(self, persistent_image: PersistentImage):
        return self.storage_path.joinpath(persistent_image.os_identifier)

    async def create_thumbnail(self, image: PersistentImage, size=THUMBNAIL_SIZE) -> None:
        image_file = self.image_dir(image).joinpath(image.name)
        with Image.open(image_file) as im:
            im.thumbnail(size)
            return im.save(image_file.parent.joinpath(image.thumb_name), "PNG")


image_storage: ImageStore = ImageStore()
