from dataclasses import dataclass, field
from enum import Enum

from api.model.id_gen import generatorFactoryInstance


@dataclass
class PersistentImage:
    os_identifier: str
    identifier: str = field(default_factory=generatorFactoryInstance.instanciator)
    is_header: bool = False

    @property
    def thumb_name(self) -> str:
        return f'{self.identifier}.thumb'

    @property
    def header_name(self) -> str:
        return f'{self.identifier}.header'

    @property
    def full_name(self) -> str:
        return str(self.identifier)


@dataclass(kw_only=True)
class SessionImage(PersistentImage):
    session_identifier: str


@dataclass
class Details:
    description: str


@dataclass
class ImageDetails(Details):
    image_identifier: str


@dataclass
class HeaderData:
    is_header: bool


@dataclass
class WithHeaderImages:
    header_images: list[PersistentImage]


class ImageType(Enum):
    full: str = 'full'
    thumb: str = 'thumb'
    header: str = 'header'

    def filename(self, image: PersistentImage):
        return getattr(image, f'{self.value}_name')


image_type_sizes = {
    ImageType.thumb: (150, 150),
    ImageType.header: (300, 300),
}
