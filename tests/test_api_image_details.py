from unittest import TestCase

from fastapi.testclient import TestClient

from api.registry.image_details import image_details_registry
from api.routes import app


class TestRestEndpoints(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.test_client = TestClient(app)
        image_details_registry.deleteAll()

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

        patch_response = self.test_client.put('/os/os-123/i/i-123/details',
                                              json={'description': 'other-test-description'})
        self.assertEqual(200, patch_response.status_code, patch_response.content)
        response = self.test_client.get('/os/os-123/i/i-123/details')
        self.assertEqual(200, response.status_code, response.content)
        self.assertDictEqual({
            'description': 'other-test-description',
            'image_identifier': 'i-123'
        }, response.json(), response.json())
