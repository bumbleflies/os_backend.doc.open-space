from dataclasses import dataclass, field

from api.model.id_gen import generatorFactoryInstance


@dataclass
class PersistentImage:
    identifier: str = field(init=False, default_factory=generatorFactoryInstance.instanciator)
    os_identifier: str
