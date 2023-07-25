import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

import uuid as uuid
import uvicorn as uvicorn
from dacite import from_dict, Config
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from os import listdir

app = FastAPI()

os_storage = Path('os/')
if not os_storage.exists():
    os_storage.mkdir()

origins = [
    "http://localhost:3000",
    "http://open-space-app.servyy.duckdns.org",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


@app.get('/health')
def health():
    return {'success': True}


@dataclass
class Location:
    lat: float
    lng: float


@dataclass
class OpenSpaceData:
    title: str
    start_date: datetime
    end_date: datetime
    location: Location


@dataclass
class OpenSpacePersistent(OpenSpaceData):
    identifier: str

    @classmethod
    def from_data(cls, os: OpenSpaceData):
        return OpenSpacePersistent(identifier=str(uuid.uuid4()), title=os.title, start_date=os.start_date,
                                   end_date=os.end_date,
                                   location=os.location)


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


if __name__ == '__main__':
    uvicorn.run("app:app", host='0.0.0.0', port=5000, reload=True)
