from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Mapping, Any

from dacite import from_dict, Config

from api.model.id_gen import generatorFactoryInstance
from api.model.image_data import PersistentImage, WithHeaderImages


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


@dataclass
class PersistentOpenSpaceDataWithHeader(WithHeaderImages, PersistentOpenSpaceData):
    @classmethod
    def from_os_header(cls, os: PersistentOpenSpaceData, header_images: list[PersistentImage]):
        os_dict = asdict(os)
        os_dict['header_images'] = []
        os_with_header = from_dict(data_class=cls, data=os_dict)
        os_with_header.header_images.extend(header_images)
        return os_with_header


def dict_to_os_data(os: Mapping[str, Any]):
    return from_dict(data_class=PersistentOpenSpaceData, data=os, config=Config(type_hooks={
        datetime: datetime.fromisoformat
    }))
