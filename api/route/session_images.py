from fastapi import APIRouter, UploadFile
from starlette import status

from api.model.image_data import SessionImage
from registry.session import session_registry
from store.image import image_storage

session_images_router = APIRouter(
    prefix='/os/{os_identifier}/s/{session_identifier}/i',
    tags=['session', 'image']
)


@session_images_router.post('/', status_code=status.HTTP_201_CREATED)
async def add_session_image(os_identifier: str, session_identifier: str, image: UploadFile) -> SessionImage:
    if session_registry.has_session(os_identifier, session_identifier):
        session_image = SessionImage(session_identifier=session_identifier, os_identifier=os_identifier)
        await image_storage.save(image, session_image)
        return session_image
