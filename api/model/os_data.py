from dataclasses import dataclass, field
from datetime import datetime

from api.model.id_gen import generatorFactoryInstance


@dataclass
class Location:
    lat: float
    lng: float


@dataclass
class TransientOpenSpaceData:
    title: str
    start_date: datetime
    end_date: datetime
    location: Location


@dataclass
class PersistentOpenSpaceData(TransientOpenSpaceData):
    identifier: str = field(init=False, default_factory=generatorFactoryInstance.instanciator)

    @classmethod
    def from_data(cls, os: TransientOpenSpaceData):
        return PersistentOpenSpaceData(title=os.title, start_date=os.start_date,
                                       end_date=os.end_date,
                                       location=os.location)
