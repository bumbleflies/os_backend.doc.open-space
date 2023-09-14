from pathlib import Path

from fastapi import APIRouter
from starlette.responses import FileResponse

loadtest_router = APIRouter(
    prefix='/loaderio-8754cc1aef698fecab6cfcb2185850fe',
    tags=['loadtest']
)


@loadtest_router.get('/')
def get_loader_id():
    return FileResponse(Path('store/').joinpath('loader.key'))
