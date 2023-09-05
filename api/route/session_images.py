from fastapi import APIRouter, UploadFile
from starlette import status
from starlette.responses import FileResponse

from api.model.image_data import SessionImage
from registry.session import session_registry
from registry.session_images import session_images_registry
from store.image import image_storage

session_images_router = APIRouter(
    prefix='/os/{os_identifier}/s/{session_identifier}/i',
    tags=['session', 'image']
)


@session_images_router.post('/', status_code=status.HTTP_201_CREATED)
async def add_session_image(os_identifier: str, session_identifier: str, image: UploadFile) -> SessionImage:
    if session_registry.has_session(os_identifier, session_identifier):
        session_image = SessionImage(session_identifier=session_identifier, os_identifier=os_identifier)
        session_images_registry.add_session_image(session_image)
        await image_storage.save(image, session_image)
        return session_image


@session_images_router.get('/')
async def get_session_images(os_identifier: str, session_identifier: str) -> list[SessionImage]:
    return session_images_registry.get_for_session(os_identifier, session_identifier)


@session_images_router.get('/{image_identifier}')
async def get_session_image(os_identifier: str, session_identifier: str, image_identifier: str):
    session_image = SessionImage(os_identifier=os_identifier, session_identifier=session_identifier,
                                 identifier=image_identifier)
    if session_images_registry.has_image(session_image):
        return FileResponse(image_storage.get(session_image))
