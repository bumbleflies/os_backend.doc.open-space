from dataclasses import asdict

from fastapi import APIRouter
from more_itertools import one
from starlette import status

from api.model.session_data import SessionData, TransientSessionData
from registry.session import session_registry

session_router = APIRouter(
    prefix='/os/{os_identifier}/s',
    tags=['session']
)


@session_router.post('/', status_code=status.HTTP_201_CREATED)
async def add_session(os_identifier: str, session: TransientSessionData) -> SessionData:
    persistent_session = SessionData.from_transient(os_identifier, session)
    session_registry.add_session(persistent_session)
    return persistent_session


@session_router.get('/')
async def get_sessions(os_identifier: str)->list[SessionData]:
    return session_registry.get_all_sessions(os_identifier)


@session_router.put('/{session_identifier}')
async def update_session(os_identifier: str, session_identifier: str, session: TransientSessionData) -> SessionData:
    if session_registry.has_session(os_identifier,session_identifier):
        return session_registry.update_session(os_identifier,session_identifier,session)
