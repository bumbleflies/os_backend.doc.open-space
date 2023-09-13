from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from api.model.id_gen import generatorFactoryInstance
from api.routes import app
from registry.os import os_registry
from tests import ApiTestCase


class TestOsApi(ApiTestCase):

    def setUp(self) -> None:
        super().setUp()
        os_registry.deleteAll()
        self.test_id = '123'
        generatorFactoryInstance.generator_function = lambda: self.test_id
        self.test_client = TestClient(app)

        self.start_date = datetime(2023, 3, 4, 5, 6, 7)
        self.test_os = {
            'title': 'test title', 'start_date': self.start_date.isoformat(),
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'location': {'lat': 1, 'lng': 2}}

    def test_get_health(self):
        response = self.test_client.get('/health')
        self.assert_response(response, 200)

    def test_create_os(self):
        response = self.test_client.post('/os', json=self.test_os)

        self.assert_response(response, 201)

        self.assertDictEqual({
            'title': 'test title',
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': '123',
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
        }, response.json())

    def test_get_all_os(self):
        self.test_client.post('/os', json=self.test_os)

        response = self.test_client.get('/os')
        self.assert_response(response, 200)

        self.assertEqual(1, len(response.json()))

        self.assertDictEqual({
            'title': 'test title',
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': '123',
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
        }, response.json()[0])

    def test_get_os(self):
        create_response = self.test_client.post('/os', json=self.test_os)
        os_id = create_response.json()['identifier']
        os_response = self.test_client.get(f'/os/{os_id}')
        self.assert_response(os_response, 200)

        self.assertDictEqual({
            'title': 'test title',
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': '123',
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
        }, os_response.json())

    def test_get_not_found(self):
        self.assertEqual(404, self.test_client.get('/os/456-not-existing-456').status_code)

    def test_delete_os(self):
        response = self.test_client.post('/os', json=self.test_os)
        os_id = response.json()['identifier']
        self.test_client.delete(f'/os/{os_id}')

    def test_put_os(self):
        response = self.test_client.post('/os', json=self.test_os)
        os_id = response.json()['identifier']
        test_os_2 = dict(self.test_os)
        test_os_2['title'] = 'new title'

        put_response = self.test_client.put(f'/os/{os_id}', json=test_os_2)

        self.assert_response(put_response, 200)
        self.assertDictEqual({
            'title': 'new title',
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': '123',
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
        }, put_response.json())

    def test_put_not_found(self):
        self.assertEqual(404, self.test_client.put('/os/456-not-existing-456', json=self.test_os).status_code)

    def test_get_os_with_header_image(self):
        create_response = self.test_client.post('/os', json=self.test_os)
        os_id = create_response.json()['identifier']
        upload_response = self.upload_os_image(os_identifier=os_id)
        image_id = upload_response.json()['identifier']
        patch_response = self.test_client.patch(f'/os/{os_id}/i/{image_id}', json={'is_header': True})
        self.assert_response(patch_response, 204)
        os_response = self.test_client.get(f'/os/{os_id}?with_header_images=true')
        self.assert_response(os_response, 200)

        self.assertDictEqual({
            'title': 'test title',
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': '123',
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
            'header_images': [{'identifier': 'i-123',
                               'is_header': True,
                               'os_identifier': '123'}]
        }, os_response.json())
