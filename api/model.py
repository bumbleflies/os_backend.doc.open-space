from dataclasses import dataclass
from datetime import datetime

import uuid as uuid


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
