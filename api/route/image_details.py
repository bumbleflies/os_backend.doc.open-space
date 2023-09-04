from fastapi import APIRouter
from starlette import status
from starlette.responses import Response

from api.model.image_data import Details, ImageDetails
from registry.image_details import image_details_registry

image_details_router = APIRouter(
    prefix='/os/{os_identifier}/i/{image_identifier}',
    tags=['image_details']
)


@image_details_router.put('/details', status_code=status.HTTP_201_CREATED)
async def add_image_details(os_identifier: str, image_identifier: str, details: Details, response: Response):
    image_details = ImageDetails(details.description, image_identifier)
    if image_details_registry.has_image_details(image_identifier):
        response.status_code = status.HTTP_200_OK
        return image_details_registry.update_image_details(image_details)
    else:
        return image_details_registry.add_details(image_details)


@image_details_router.get('/details')
async def get_image_details(os_identifier: str, image_identifier: str, response: Response):
    if image_details_registry.has_image_details(image_identifier):
        return image_details_registry.get_by_image_identifier(image_identifier)
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'message': 'Invalid Image Identifier'}


@image_details_router.delete('/details', status_code=status.HTTP_204_NO_CONTENT)
async def delete_image_details(image_identifier: str):
    image_details_registry.delete_by_image_identifier(image_identifier)
