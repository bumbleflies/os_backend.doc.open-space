import uuid as uuid


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
