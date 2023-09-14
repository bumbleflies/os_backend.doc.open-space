import asyncio
from asyncio import Task
from os import listdir
from pathlib import Path

from PIL import Image
from fastapi import UploadFile

from api.model.image_data import PersistentImage, ImageType, image_type_sizes


class ImageFilenameResolver:
    def __init__(self, base_path: Path, image: PersistentImage):
        self.base_path = base_path
        self.image = image

    def as_type(self, _type: ImageType):
        return self.base_path.joinpath(_type.filename(self.image))


class ImageSizesCreator:
    def __init__(self, file_resolver: ImageFilenameResolver):
        self.file_resolver = file_resolver

    async def resize_to(self, image: PersistentImage, _type: ImageType) -> None:
        with Image.open(self.file_resolver.as_type(ImageType.full)) as im:
            im.thumbnail(image_type_sizes[_type])
            return im.save(self.file_resolver.as_type(_type), "PNG")

    async def resize_all(self, image: PersistentImage):
        return asyncio.wait((
            asyncio.create_task(self.resize_to(image, ImageType.thumb)),
            asyncio.create_task(self.resize_to(image, ImageType.header))
        ))


class ImageStore:
    def __init__(self, path='img'):
        self._image_storage = Path(path)

    async def save(self, image: UploadFile, persistent_image: PersistentImage) -> (PersistentImage, Task[None]):
        os_path = self.image_dir(persistent_image)
        if not os_path.exists():
            os_path.mkdir()
        with os_path.joinpath(persistent_image.full_name) as image_file:
            image_file.write_bytes(await image.read())

        return persistent_image, await ImageSizesCreator(self.get(persistent_image)).resize_all(persistent_image)

    def get(self, persistent_image: PersistentImage):
        return ImageFilenameResolver(self.image_dir(persistent_image), persistent_image)

    def delete(self, persistent_image: PersistentImage):
        for _type in ImageType:
            self.get(persistent_image).as_type(_type).unlink(missing_ok=True)
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


image_storage: ImageStore = ImageStore()
