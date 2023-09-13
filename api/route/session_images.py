from fastapi import APIRouter, UploadFile
from starlette import status
from starlette.responses import FileResponse, Response

from api.model.error import ErrorMessage
from api.model.image_data import SessionImage, HeaderData
from registry.session import session_registry
from registry.session_images import session_images_registry
from store.image import image_storage

session_images_router = APIRouter(
    prefix='/os/{os_identifier}/s/{session_identifier}/i',
    tags=['session', 'image']
)


@session_images_router.post('/', status_code=status.HTTP_201_CREATED)
async def add_session_image(os_identifier: str, session_identifier: str, image: UploadFile, response: Response):
    if session_registry.has_session(os_identifier, session_identifier):
        session_image = SessionImage(session_identifier=session_identifier, os_identifier=os_identifier)
        session_images_registry.add_session_image(session_image)
        await image_storage.save(image, session_image)
        return session_image
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorMessage(f'No Session found for {session_identifier}')


@session_images_router.get('/')
async def get_session_images(os_identifier: str, session_identifier: str, only_header: bool = False) \
        -> list[SessionImage]:
    return session_images_registry.get_for_session(os_identifier, session_identifier,only_header)


@session_images_router.get('/{image_identifier}')
async def get_session_image(os_identifier: str, session_identifier: str, image_identifier: str, response: Response):
    session_image = SessionImage(os_identifier=os_identifier, session_identifier=session_identifier,
                                 identifier=image_identifier)
    if session_images_registry.has_image(session_image):
        return FileResponse(image_storage.get(session_image))
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorMessage(f'No Image found for {image_identifier}')


@session_images_router.delete('/{image_identifier}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_session_image(os_identifier: str, session_identifier: str, image_identifier: str, response: Response):
    session_image = SessionImage(os_identifier=os_identifier, session_identifier=session_identifier,
                                 identifier=image_identifier)
    if session_images_registry.has_image(session_image):
        session_images_registry.delete(session_image)
        return image_storage.delete(session_image)


@session_images_router.patch('/{image_identifier}', status_code=status.HTTP_204_NO_CONTENT)
async def make_header_session_image(os_identifier: str, session_identifier: str, image_identifier: str,
                                    header_data: HeaderData):
    if header_data.is_header:
        # only allow one header
        for session_image in session_images_registry.getByQuery({'session_identifier': session_identifier}):
            session_images_registry.updateById(session_image.get(session_images_registry.id_fieldname), {'is_header': False})
    session_image = SessionImage(os_identifier=os_identifier, session_identifier=session_identifier,
                                 identifier=image_identifier)
    session_images_registry.update_header(session_image, header_data)
