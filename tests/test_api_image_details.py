from pathlib import Path
from unittest import TestCase

from fastapi.testclient import TestClient

from api.routes import app
from registry.image_details import image_details_registry


class TestImageDetailsApi(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.test_client = TestClient(app)
        image_details_registry.deleteAll()
        self.fixture_image = Path('tests').joinpath('fixtures/test-image.png')

    def test_add_image_description(self):
        patch_response = self.test_client.put('/os/os-123/i/i-123/details', json={'description': 'test-description'})
        self.assertEqual(201, patch_response.status_code, patch_response.content)
        response = self.test_client.get('/os/os-123/i/i-123/details')
        self.assertEqual(200, response.status_code, response.content)
        self.assertDictEqual({
            'description': 'test-description',
            'image_identifier': 'i-123'
        }, response.json(), response.json())

    def test_get_non_existing_details(self):
        response = self.test_client.get('/os/os-123/i/i-non-existing/details')
        self.assertEqual(404, response.status_code, response.content)

    def test_update_image_description(self):
        create_response = self.test_client.put('/os/os-123/i/i-123/details', json={'description': 'test-description'})
        self.assertEqual(201, create_response.status_code, create_response.content)
        response = self.test_client.get('/os/os-123/i/i-123/details')
        self.assertEqual(200, response.status_code, response.content)
        self.assertDictEqual({
            'description': 'test-description',
            'image_identifier': 'i-123'
        }, response.json(), response.json())

        put_response = self.test_client.put('/os/os-123/i/i-123/details',
                                              json={'description': 'other-test-description'})
        self.assertEqual(200, put_response.status_code, put_response.content)
        response = self.test_client.get('/os/os-123/i/i-123/details')
        self.assertEqual(200, response.status_code, response.content)
        self.assertDictEqual({
            'description': 'other-test-description',
            'image_identifier': 'i-123'
        }, response.json(), response.json())

    def test_delete_image_details(self):
        create_response = self.test_client.put('/os/os-123/i/i-123/details', json={'description': 'test-description'})
        self.assertEqual(201, create_response.status_code, create_response.content)

        delete_response = self.test_client.delete('/os/os-123/i/i-123/details')
        self.assertEqual(204, delete_response.status_code, delete_response.content)

    def test_details_deleted_when_image_deleted(self):
        with open(self.fixture_image, 'rb') as image_file:
            image_response = self.test_client.post('/os/os-123/i/', files={'image': image_file})
            self.assertEqual(201, image_response.status_code, image_response.content)

        image_id = image_response.json()['identifier']

        details_response = self.test_client.put(f'/os/os-123/i/{image_id}/details',
                                                json={'description': 'test-description'})
        self.assertEqual(201, details_response.status_code, details_response.content)

        delete_response = self.test_client.delete(f'/os/os-123/i/{image_id}')
        self.assertEqual(204, delete_response.status_code, delete_response.content)

        deleted_get_response = self.test_client.get(f'/os/os-123/i/{image_id}/details')
        self.assertEqual(404, deleted_get_response.status_code, deleted_get_response.content)
