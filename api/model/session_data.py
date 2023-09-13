from dataclasses import field, dataclass, asdict
from datetime import datetime

from dacite import from_dict

from api.model.id_gen import generatorFactoryInstance
from api.model.image_data import WithHeaderImages, PersistentImage


@dataclass
class TransientSessionData:
    title: str
    start_date: datetime
    end_date: datetime


@dataclass
class SessionData(TransientSessionData):
    os_identifier: str
    identifier: str = field(init=False, default_factory=generatorFactoryInstance.instanciator)

    @classmethod
    def from_transient(cls, os_identifier: str, transient_session: TransientSessionData):
        return SessionData(os_identifier=os_identifier, **transient_session.__dict__)


@dataclass
class SessionDataWithHeader(WithHeaderImages, SessionData):
    @classmethod
    def from_session_and_header_image(cls, session: SessionData, header_images: list[PersistentImage]):
        session_dict = asdict(session)
        session_dict['header_images'] = []
        session_with_header = from_dict(data_class=cls, data=session_dict)
        session_with_header.header_images.extend(header_images)
        return session_with_header
