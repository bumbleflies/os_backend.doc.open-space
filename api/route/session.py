from fastapi import APIRouter, Depends
from fastapi_auth0 import Auth0User
from starlette import status
from starlette.responses import Response

from api.model.error import ErrorMessage
from api.model.session_data import SessionData, TransientSessionData, SessionDataWithHeader
from api.route.auth import auth, Permission
from registry.session import session_registry
from registry.session_images import session_images_registry

session_router = APIRouter(
    prefix='/os/{os_identifier}/s',
    tags=['session']
)


@session_router.post('/', status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.authcode_scheme)])
async def add_session(os_identifier: str, session: TransientSessionData,
                      user: Auth0User = Depends(auth.get_user)) -> SessionData:
    persistent_session = SessionData.from_transient(os_identifier, session, user.id)
    session_registry.add_session(persistent_session)
    return persistent_session


@session_router.get('/')
async def get_sessions(os_identifier: str, with_header_images: bool = False) \
        -> (list[SessionData] |
            list[SessionDataWithHeader]):
    all_sessions = session_registry.get_all_sessions(os_identifier)
    if with_header_images:
        all_session_with_header = []
        for session in all_sessions:
            session_images = session_images_registry.get_for_session(os_identifier=session.os_identifier,
                                                                     session_identifier=session.identifier,
                                                                     only_header=with_header_images)
            all_session_with_header.append(SessionDataWithHeader.from_session_and_header_image(session, session_images))
        all_sessions = all_session_with_header
    return all_sessions


@session_router.put('/{session_identifier}', dependencies=[Depends(auth.authcode_scheme)])
async def update_session(os_identifier: str, session_identifier: str, session: TransientSessionData,
                         response: Response) -> SessionData | ErrorMessage:
    if session_registry.has_session(os_identifier, session_identifier):
        return session_registry.update_session(os_identifier, session_identifier, session)
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorMessage('Invalid OpenSpace Identifier')


@session_router.get('/{session_identifier}')
async def get_session(os_identifier: str, session_identifier: str, response: Response) -> SessionData | ErrorMessage:
    if session_registry.has_session(os_identifier, session_identifier):
        return session_registry.get_session(os_identifier, session_identifier)
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorMessage('Invalid OpenSpace Identifier')


@session_router.delete('/{session_identifier}', status_code=status.HTTP_204_NO_CONTENT,
                       dependencies=[Depends(auth.authcode_scheme)])
async def delete_session(os_identifier: str, session=Permission('delete', get_session)) -> None:
    return session_registry.delete_by_identifier(session.identifier)
