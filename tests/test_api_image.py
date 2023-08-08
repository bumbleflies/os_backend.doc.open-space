from pathlib import Path
from unittest import TestCase

from fastapi.testclient import TestClient

from api.model.id_gen import generatorFactoryInstance
from api.routes import app
from api.store.image import image_registry


class TestRestEndpoints(TestCase):

    def provide_testfile(self, os_identifier='os-123', i_identifier='i-123'):
        self.test_id = i_identifier
        with open(self.fixture_image, 'rb') as image_file:
            test_client_post = self.test_client.post(f'/os/{os_identifier}/i/', files={'image': image_file})
        self.assertEqual(201, test_client_post.status_code)
        return test_client_post

    def get_test_id(self):
        return self.test_id

    def setUp(self) -> None:
        super().setUp()
        image_registry.deleteAll()
        self.test_id = '123'
        generatorFactoryInstance.generator_function = lambda: self.get_test_id()
        self.test_client = TestClient(app)
        self.fixture_image = Path('tests').joinpath('fixtures/test-image.png')

    def test_create_os_image(self):
        with open(self.fixture_image, 'rb') as image_file:
            response = self.test_client.post('/os/123/i/', files={'image': image_file})

        self.assertEqual(201, response.status_code, response.content)
        self.assertEqual('123', response.json()['identifier'], response.json())
        self.assertEqual('123', response.json()['os_identifier'], response.json())

    def test_get_os_image(self):
        self.provide_testfile()
        response = self.test_client.get('/os/os-123/i/i-123')
        self.assertEqual(200, response.status_code, response.content)

    def test_get_os_images(self):
        self.provide_testfile()
        response = self.test_client.get('/os/os-123/i/')
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual(1, len(response.json()), response.json())
        self.assertDictEqual({
            'identifier': 'i-123',
            'os_identifier': 'os-123',
            'is_header': False,
        }, response.json()[0], response.json())

    def test_delete_os_image(self):
        self.provide_testfile()
        response = self.test_client.delete('/os/os-123/i/i-123')
        self.assertEqual(204, response.status_code)

    def test_make_header(self):
        self.provide_testfile()
        patch_response = self.test_client.patch('/os/os-123/i/i-123', json={'is_header': True})
        self.assertEqual(204, patch_response.status_code, patch_response.content)
        response = self.test_client.get('/os/os-123/i/')
        self.assertEqual(200, response.status_code, response.content)
        self.assertDictEqual({
            'identifier': 'i-123',
            'os_identifier': 'os-123',
            'is_header': True,
        }, response.json()[0], response.json())

    def test_get_header_image(self):
        self.provide_testfile()
        self.provide_testfile(i_identifier='i-345')
        patch_response = self.test_client.patch('/os/os-123/i/i-345', json={'is_header': True})
        self.assertEqual(204, patch_response.status_code, patch_response.content)
        response = self.test_client.get('/os/os-123/i/?only_header=True')
        self.assertEqual(200, response.status_code, response.content)
        self.assertDictEqual({
            'identifier': 'i-345',
            'os_identifier': 'os-123',
            'is_header': True,
        }, response.json()[0], response.json())

    def test_only_one_header_image(self):
        self.provide_testfile(i_identifier='i-123')
        self.provide_testfile(i_identifier='i-345')
        self.assertEqual(204, self.test_client.patch('/os/os-123/i/i-123', json={'is_header': True}).status_code)
        self.assertEqual(204, self.test_client.patch('/os/os-123/i/i-345', json={'is_header': True}).status_code)
        response = self.test_client.get('/os/os-123/i/?only_header=True')
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual(1, len(response.json()), response.json())
