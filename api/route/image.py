from os import listdir
from pathlib import Path

from fastapi import UploadFile, APIRouter
from starlette import status
from starlette.responses import Response, FileResponse

from api.model.image_data import PersistentImage, HeaderData
from api.store.image import image_registry


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
        return self.storage.joinpath(persistent_image.os_identifier).joinpath(persistent_image.identifier)

    def delete(self, persistent_image: PersistentImage):
        if self.get(persistent_image).exists():
            self.get(persistent_image).unlink()

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
    persistent_image = PersistentImage(os_identifier)
    image_registry.add_image(persistent_image)
    return await image_storage.save(image, persistent_image)


@image_router.get('/')
async def get_os_images(os_identifier: str, only_header: bool = False) -> list[PersistentImage]:
    return list(filter(lambda i: not only_header or i.is_header, image_registry.get_for_os(os_identifier)))


@image_router.get('/{image_identifier}')
async def get_os_image(os_identifier: str, image_identifier: str, response: Response):
    persistent_image = PersistentImage(os_identifier, image_identifier)
    if image_registry.has_image(persistent_image):
        return FileResponse(image_storage.get(persistent_image))
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'message': 'Invalid Image Identifier'}


@image_router.delete('/{image_identifier}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(os_identifier: str, image_identifier: str) -> None:
    image_registry.delete_by_identifier(image_identifier)
    image_storage.delete(PersistentImage(os_identifier, image_identifier))


@image_router.patch('/{image_identifier}', status_code=status.HTTP_204_NO_CONTENT)
async def make_header_image(os_identifier: str, image_identifier: str, header_data: HeaderData):
    if header_data.is_header:
        # only allow one header
        for os_image in image_registry.getByQuery({'os_identifier': os_identifier}):
            image_registry.updateById(os_image.get('id'), {'is_header': False})
    image_registry.updateById(image_registry.get_image(PersistentImage(os_identifier, image_identifier)).get('id'),
                              {'is_header': header_data.is_header})
