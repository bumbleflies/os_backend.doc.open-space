from datetime import datetime, timedelta
from datetime import datetime, timedelta
from unittest import TestCase

from fastapi.testclient import TestClient

from api.model import generatorFactoryInstance
from api.routes import app, os_storage
from os import listdir


class TestRestEndpoints(TestCase):

    def setUp(self) -> None:
        super().setUp()
        generatorFactoryInstance.generator_function = lambda: '123'
        self.test_client = TestClient(app)
        for file in listdir(os_storage):
            os_storage.joinpath(file).unlink()

        self.start_date = datetime.now()
        self.test_os = {
            'title': 'test title', 'start_date': self.start_date.isoformat(),
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'location': {'lat': 1, 'lng': 2}}

    def test_get_health(self):
        response = self.test_client.get('/health')
        self.assertEqual(200, response.status_code)

    def test_create_os(self):
        response = self.test_client.post('/os', json=self.test_os)

        self.assertEqual(201, response.status_code, response.content)

        self.assertEqual({
            'title': 'test title',
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': '123',
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
        }, response.json())
