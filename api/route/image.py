from dacite import from_dict
from fastapi import UploadFile, APIRouter, Depends
from fastapi_auth0 import Auth0User
from starlette import status
from starlette.responses import Response, FileResponse

from api.model.error import ErrorMessage
from api.model.image_data import PersistentImage, HeaderData, ImageType
from api.route.auth import auth, Permission
from api.route.image_details import delete_image_details
from registry.image import image_registry
from store.image import image_storage

image_router = APIRouter(
    prefix='/os/{os_identifier}/i',
    tags=['image']
)


@image_router.post('/', status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.authcode_scheme)])
async def upload_os_images(os_identifier: str, image: UploadFile,
                           user: Auth0User = Depends(auth.get_user)) -> PersistentImage:
    persistent_image = PersistentImage(os_identifier, owner=user.id)
    image_registry.add_image(persistent_image)
    (saved_image, _) = await image_storage.save(image, persistent_image)
    if not image_registry.get_for_os(os_identifier, True):
        image_registry.make_header(saved_image, HeaderData(True))
    return saved_image


@image_router.get('/')
async def get_os_images(os_identifier: str, only_header: bool = False) -> list[PersistentImage]:
    return image_registry.get_for_os(os_identifier, only_header)


@image_router.get('/{image_identifier}')
async def get_os_image(os_identifier: str, image_identifier: str,
                       image_type: ImageType = ImageType.full,
                       response: Response = None):
    persistent_image = PersistentImage(os_identifier=os_identifier, identifier=image_identifier)
    if image_registry.has_image(persistent_image):

        return FileResponse(image_storage.get(persistent_image).as_type(image_type))
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorMessage('Invalid Image Identifier')


def get_image(os_identifier: str, image_identifier: str):
    persistent_image = PersistentImage(os_identifier=os_identifier, identifier=image_identifier)
    return from_dict(data_class=PersistentImage, data=image_registry.get_image(persistent_image))


@image_router.delete('/{image_identifier}', status_code=status.HTTP_204_NO_CONTENT,
                     dependencies=[Depends(auth.authcode_scheme)])
async def delete_image(image=Permission('delete', get_image)) -> None:
    image_registry.delete_by_identifier(image.identifier)
    image_storage.delete(image)
    await delete_image_details(image.identifier)


@image_router.patch('/{image_identifier}', status_code=status.HTTP_204_NO_CONTENT)
async def make_header_image(os_identifier: str, image_identifier: str, header_data: HeaderData):
    if header_data.is_header:
        # only allow one header
        for os_image in image_registry.getByQuery({'os_identifier': os_identifier}):
            image_registry.updateById(os_image.get(image_registry.id_fieldname), {'is_header': False})
    image_registry.make_header(PersistentImage(os_identifier=os_identifier, identifier=image_identifier), header_data)
