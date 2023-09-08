from os import listdir
from pathlib import Path

from api.model.id_gen import generatorFactoryInstance
from registry.image import image_registry
from tests import ApiTestCase


class TestImageApi(ApiTestCase):

    def get_test_id(self):
        return self.test_id

    def setUp(self) -> None:
        super().setUp()
        image_registry.deleteAll()
        self.test_id = '123'
        generatorFactoryInstance.generator_function = lambda: self.get_test_id()

    def test_create_os_image(self):
        with open(self.fixture_image, 'rb') as image_file:
            response = self.test_client.post('/os/123/i/', files={'image': image_file})

        self.assert_response(response, 201)
        self.assertEqual('123', response.json()['identifier'], response.json())
        self.assertEqual('123', response.json()['os_identifier'], response.json())

    def test_get_os_image(self):
        self.upload_os_image()
        response = self.test_client.get('/os/os-123/i/i-123')
        self.assert_response(response, 200)

    def test_get_os_images(self):
        self.upload_os_image()
        response = self.test_client.get('/os/os-123/i/')
        self.assert_response(response, 200)
        self.assertEqual(1, len(response.json()), response.json())
        self.assertDictEqual({
            'identifier': 'i-123',
            'os_identifier': 'os-123',
            'is_header': False,
        }, response.json()[0], response.json())

    def test_delete_os_image(self):
        self.upload_os_image()
        response = self.test_client.delete('/os/os-123/i/i-123')
        self.assert_response(response, 204)

    def test_make_header(self):
        self.upload_os_image()
        patch_response = self.test_client.patch('/os/os-123/i/i-123', json={'is_header': True})
        self.assert_response(patch_response, 204)
        response = self.test_client.get('/os/os-123/i/')
        self.assert_response(response, 200)
        self.assertDictEqual({
            'identifier': 'i-123',
            'os_identifier': 'os-123',
            'is_header': True,
        }, response.json()[0], response.json())

    def test_get_header_image(self):
        self.upload_os_image()
        self.upload_os_image(i_identifier='i-345')
        patch_response = self.test_client.patch('/os/os-123/i/i-345', json={'is_header': True})
        self.assert_response(patch_response, 204)
        response = self.test_client.get('/os/os-123/i/?only_header=True')
        self.assert_response(response, 200)
        self.assertDictEqual({
            'identifier': 'i-345',
            'os_identifier': 'os-123',
            'is_header': True,
        }, response.json()[0], response.json())

    def test_only_one_header_image(self):
        self.upload_os_image(i_identifier='i-123')
        self.upload_os_image(i_identifier='i-345')
        self.assertEqual(204, self.test_client.patch('/os/os-123/i/i-123', json={'is_header': True}).status_code)
        self.assertEqual(204, self.test_client.patch('/os/os-123/i/i-345', json={'is_header': True}).status_code)
        response = self.test_client.get('/os/os-123/i/?only_header=True')
        self.assert_response(response, 200)
        self.assertEqual(1, len(response.json()), response.json())

    def test_image_dir_is_deleted_when_empty(self):
        with open(self.fixture_image, 'rb') as image_file:
            response1 = self.test_client.post('/os/123/i/', files={'image': image_file})
            self.test_id = '345'
            response2 = self.test_client.post('/os/123/i/', files={'image': image_file})
            self.assert_response(response1, 201)
            self.assert_response(response2, 201)

        response = self.test_client.get('/os/123/i/')
        self.assert_response(response, 200)
        self.assertEqual(2, len(response.json()), response.json())
        self.assertEqual(2, len(listdir(Path('img').joinpath('123'))))
        response_del1 = self.test_client.delete('/os/123/i/123')
        self.assert_response(response_del1, 204)
        response_del2 = self.test_client.delete('/os/123/i/345')
        self.assert_response(response_del2, 204)
        self.assertFalse(Path('img').joinpath('123').exists())
