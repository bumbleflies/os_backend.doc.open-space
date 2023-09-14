from dataclasses import asdict

from fastapi import UploadFile, APIRouter
from starlette import status
from starlette.responses import Response, FileResponse

from api.model.error import ErrorMessage
from api.model.image_data import PersistentImage, HeaderData
from api.route.image_details import delete_image_details
from registry.image import image_registry
from store.image import image_storage

image_router = APIRouter(
    prefix='/os/{os_identifier}/i',
    tags=['image']
)


@image_router.post('/', status_code=status.HTTP_201_CREATED)
async def upload_os_images(os_identifier, image: UploadFile) -> PersistentImage:
    persistent_image = PersistentImage(os_identifier)
    image_registry.add_image(persistent_image)
    (saved_image, _) = await image_storage.save(image, persistent_image)
    return saved_image


@image_router.get('/')
async def get_os_images(os_identifier: str, only_header: bool = False) -> list[PersistentImage]:
    return image_registry.get_for_os(os_identifier, only_header)


@image_router.get('/{image_identifier}')
async def get_os_image(os_identifier: str, image_identifier: str, thumbnail: bool = False, response: Response = None):
    persistent_image = PersistentImage(os_identifier, image_identifier)
    if image_registry.has_image(persistent_image):
        if thumbnail:
            image_file = FileResponse(image_storage.get_thumb(persistent_image))
        else:
            image_file = FileResponse(image_storage.get(persistent_image))
        return image_file
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorMessage('Invalid Image Identifier')


@image_router.delete('/{image_identifier}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(os_identifier: str, image_identifier: str) -> None:
    image_registry.delete_by_identifier(image_identifier)
    image_storage.delete(PersistentImage(os_identifier, image_identifier))
    await delete_image_details(image_identifier)


@image_router.patch('/{image_identifier}', status_code=status.HTTP_204_NO_CONTENT)
async def make_header_image(os_identifier: str, image_identifier: str, header_data: HeaderData):
    if header_data.is_header:
        # only allow one header
        for os_image in image_registry.getByQuery({'os_identifier': os_identifier}):
            image_registry.updateById(os_image.get(image_registry.id_fieldname), {'is_header': False})
    image_registry.updateById(
        image_registry.get_image(PersistentImage(os_identifier, image_identifier)).get(image_registry.id_fieldname),
        asdict(header_data))
