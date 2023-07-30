from dataclasses import dataclass, field

from api.model.id_gen import generatorFactoryInstance


@dataclass
class PersistentImage:
    os_identifier: str
    identifier: str = field(default_factory=generatorFactoryInstance.instanciator)
