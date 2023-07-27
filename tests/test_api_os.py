from datetime import datetime, timedelta
from pathlib import Path
from unittest import TestCase

from fastapi.testclient import TestClient

from api.model.id_gen import generatorFactoryInstance
from api.routes import app, os_storage
from os import listdir


class TestRestEndpoints(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.test_id = '123'
        generatorFactoryInstance.generator_function = lambda: self.test_id
        self.test_client = TestClient(app)
        for file in listdir(os_storage):
            os_storage.joinpath(file).unlink()

        self.start_date = datetime(2023, 3, 4, 5, 6, 7)
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

        self.assertDictEqual({
            'title': 'test title',
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': '123',
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
        }, response.json())

    def test_get_os(self):
        self.test_client.post('/os', json=self.test_os)

        response = self.test_client.get('/os')
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, len(response.json()))

        self.assertDictEqual({
            'title': 'test title',
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': '123',
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
        }, response.json()[0])

    def test_delete_os(self):
        response = self.test_client.post('/os', json=self.test_os)
        os_id = response.json()['identifier']
        self.assertTrue(Path('os').joinpath(os_id).exists())
        self.test_client.delete(f'/os/{os_id}')
        self.assertFalse(Path('os').joinpath(os_id).exists())

    def test_put_os(self):
        response = self.test_client.post('/os', json=self.test_os)
        os_id = response.json()['identifier']
        test_os_2 = dict(self.test_os)
        test_os_2['title'] = 'new title'

        put_response = self.test_client.put(f'/os/{os_id}', json=test_os_2)

        self.assertEqual(200, put_response.status_code)
        self.assertDictEqual({
            'title': 'new title',
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': '123',
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
        }, put_response.json())

    def test_put_not_found(self):
        self.assertEqual(404, self.test_client.put('/os/456-not-existing-456', json=self.test_os).status_code)

