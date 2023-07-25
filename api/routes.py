import json
from dataclasses import asdict
from datetime import datetime
from os import listdir

from dacite import from_dict, Config
from starlette import status

from api.encoder import DateTimeEncoder
from api.model import OpenSpaceData, OpenSpacePersistent
from app import app, os_storage


@app.get('/health')
def health():
    return {'success': True}


@app.post('/os/', status_code=status.HTTP_201_CREATED)
async def create_os(osd: OpenSpaceData) -> OpenSpacePersistent:
    os_persistent = OpenSpacePersistent.from_data(osd)
    with open(os_storage.joinpath(os_persistent.identifier), 'w') as os_file:
        json.dump(asdict(os_persistent), os_file, cls=DateTimeEncoder)
    return os_persistent


@app.get('/os/')
async def get_open_spaces() -> list[OpenSpacePersistent]:
    os_persistent = []
    for os_filename in listdir(os_storage):
        with open(os_storage.joinpath(os_filename), 'r') as os_file:
            os_persistent.append(
                from_dict(data_class=OpenSpacePersistent, data=json.load(os_file), config=Config(type_hooks={
                    datetime: datetime.fromisoformat
                })))
    return os_persistent


@app.delete('/os/{identifier}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_open_space(identifier: str):
    os_path = os_storage.joinpath(identifier)
    if os_path.exists():
        os_path.unlink()
