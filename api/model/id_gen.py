import uuid as uuid


class IdGeneratorFactory:
    def __init__(self):
        self.generator_function = self.generate

    def generate(self) -> str:
        return str(uuid.uuid4())

    def instanciator(self) -> str:
        def do_generate() -> str:
            return self.generator_function()

        return do_generate()


generatorFactoryInstance: IdGeneratorFactory = IdGeneratorFactory()
