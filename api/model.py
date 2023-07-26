from dataclasses import dataclass, field
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


class IdGeneratorFactory:
    def __init__(self):
        self.generator_function = self.generate

    def generate(self):
        return str(uuid.uuid4())

    def instanciator(self):
        def do_generate():
            return self.generator_function()

        return do_generate()


generatorFactoryInstance = IdGeneratorFactory()


@dataclass
class OpenSpacePersistent(OpenSpaceData):
    identifier: str = field(init=False, default_factory=generatorFactoryInstance.instanciator)

    @classmethod
    def from_data(cls, os: OpenSpaceData):
        return OpenSpacePersistent(title=os.title, start_date=os.start_date,
                                   end_date=os.end_date,
                                   location=os.location)
