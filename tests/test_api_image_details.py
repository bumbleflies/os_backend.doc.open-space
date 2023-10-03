from registry.image_details import image_details_registry
from tests import AuthEnabledApiTestCase


class TestImageDetailsApi(AuthEnabledApiTestCase):

    def setUp(self) -> None:
        super().setUp()
        image_details_registry.deleteAll()

    def test_add_image_description(self):
        patch_response = self.test_client.put('/os/os-123/i/i-123/details', json={'description': 'test-description'})
        self.assert_response(patch_response, 201)
        response = self.test_client.get('/os/os-123/i/i-123/details')
        self.assert_response(response, 200)
        self.assertDictEqual({
            'description': 'test-description',
            'image_identifier': 'i-123'
        }, response.json(), response.json())

    def test_get_non_existing_details(self):
        response = self.test_client.get('/os/os-123/i/i-non-existing/details')
        self.assert_response(response, 404)

    def test_update_image_description(self):
        create_response = self.test_client.put('/os/os-123/i/i-123/details', json={'description': 'test-description'})
        self.assert_response(create_response, 201)
        response = self.test_client.get('/os/os-123/i/i-123/details')
        self.assert_response(response, 200)
        self.assertDictEqual({
            'description': 'test-description',
            'image_identifier': 'i-123'
        }, response.json(), response.json())

        put_response = self.test_client.put('/os/os-123/i/i-123/details',
                                            json={'description': 'other-test-description'})
        self.assert_response(put_response, 200)
        response = self.test_client.get('/os/os-123/i/i-123/details')
        self.assert_response(response, 200)
        self.assertDictEqual({
            'description': 'other-test-description',
            'image_identifier': 'i-123'
        }, response.json(), response.json())

    def test_delete_image_details(self):
        create_response = self.test_client.put('/os/os-123/i/i-123/details', json={'description': 'test-description'})
        self.assert_response(create_response, 201)

        delete_response = self.test_client.delete('/os/os-123/i/i-123/details')
        self.assert_response(delete_response, 204)

    def test_details_deleted_when_image_deleted(self):
        image_id = self.upload_os_image('os-123')

        details_response = self.auth_test_client.put(f'/os/os-123/i/{image_id}/details',
                                                     json={'description': 'test-description'})
        self.assert_response(details_response, 201)

        delete_response = self.auth_test_client.delete(f'/os/os-123/i/{image_id}')
        self.assert_response(delete_response, 204)

        deleted_get_response = self.test_client.get(f'/os/os-123/i/{image_id}/details')
        self.assert_response(deleted_get_response, 404)
