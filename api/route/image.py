from os import listdir
from pathlib import Path

from fastapi import UploadFile, APIRouter
from starlette import status
from starlette.responses import Response, FileResponse

from api.model.image_data import PersistentImage


class ImageStore:
    def __init__(self, path='img'):
        self._image_storage = Path('img/')

    async def save(self, image: UploadFile, persistent_image: PersistentImage):
        os_path = self.storage.joinpath(persistent_image.os_identifier)
        if not os_path.exists():
            os_path.mkdir()
        with os_path.joinpath(persistent_image.identifier) as image_file:
            image_file.write_bytes(await image.read())
        return persistent_image

    def load(self, os_identifier: str) -> list[PersistentImage]:
        os_image_path = self.storage.joinpath(os_identifier)
        if os_image_path.exists():
            return [PersistentImage(os_identifier, identifier=pi) for pi in listdir(os_image_path)]
        else:
            return []

    def get(self, persistent_image: PersistentImage):
        return self._image_storage.joinpath(persistent_image.os_identifier).joinpath(persistent_image.identifier)

    @property
    def storage(self):
        if not self._image_storage.exists():
            self._image_storage.mkdir()
        return self._image_storage


image_storage = ImageStore()

image_router = APIRouter(
    prefix='/os/{os_identifier}/i',
    tags=['image']
)


@image_router.post('/', status_code=status.HTTP_201_CREATED)
async def upload_os_images(os_identifier, image: UploadFile) -> PersistentImage:
    return await image_storage.save(image, PersistentImage(os_identifier))


@image_router.get('/')
async def get_os_images(os_identifier: str) -> list[PersistentImage]:
    return image_storage.load(os_identifier)


@image_router.get('/{image_identifier}')
async def get_os_image(os_identifier, image_identifier, response: Response):
    image_path = image_storage.get(PersistentImage(os_identifier, image_identifier))
    if image_path.exists():
        return FileResponse(image_path)
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'message': 'Invalid Image Identifier'}
