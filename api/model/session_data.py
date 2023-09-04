from dataclasses import field, dataclass
from datetime import datetime

from api.model.id_gen import generatorFactoryInstance


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
