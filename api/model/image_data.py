from dataclasses import dataclass, field

from api.model.id_gen import generatorFactoryInstance


@dataclass
class PersistentImage:
    os_identifier: str
    identifier: str = field(default_factory=generatorFactoryInstance.instanciator)
    is_header: bool = False


@dataclass
class Details:
    description: str


@dataclass
class ImageDetails(Details):
    image_identifier: str


@dataclass
class HeaderData:
    is_header: bool
