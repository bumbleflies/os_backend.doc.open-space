from pathlib import Path
from shutil import copyfile
from unittest import TestCase

from fastapi.testclient import TestClient

from api.model.id_gen import generatorFactoryInstance
from api.routes import app, image_storage
from os import listdir


class TestRestEndpoints(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.test_id = '123'
        generatorFactoryInstance.generator_function = lambda: self.test_id
        self.test_client = TestClient(app)
        for file in listdir(image_storage):
            image_storage.joinpath(file).unlink()
        self.fixture_image = Path('tests').joinpath('fixtures/test-image.png')

    def test_create_os(self):
        with open(self.fixture_image, 'rb') as image_file:
            response = self.test_client.post('/os/123/images/', files={'image': image_file})

        self.assertEqual(201, response.status_code, response.content)
        self.assertEqual('123', response.json()['identifier'], response.json())
        self.assertEqual('123', response.json()['os_identifier'], response.json())

    def test_get_os(self):
        copyfile(self.fixture_image, image_storage.joinpath('123'))
        response = self.test_client.get('/os/123/images/123')
        self.assertEqual(200, response.status_code, response.content)
