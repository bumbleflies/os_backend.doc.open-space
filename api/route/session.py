from fastapi import APIRouter
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
async def get_sessions(os_identifier: str):
    return session_registry.get_all_sessions(os_identifier)
