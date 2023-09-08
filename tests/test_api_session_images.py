from datetime import datetime, timedelta
from pathlib import Path
from unittest import TestCase

from fastapi.testclient import TestClient

from api.model.id_gen import generatorFactoryInstance
from api.model.session_data import SessionData
from api.routes import app
from registry.session import session_registry
from registry.session_images import session_images_registry


class TestSessionImagesApi(TestCase):

    def setUp(self) -> None:
        self.test_client = TestClient(app)
        self.start_date = datetime(2023, 3, 4, 5, 6, 7)
        self.test_id = '345'
        generatorFactoryInstance.generator_function = lambda: self.test_id
        session_registry.deleteAll()
        session_images_registry.deleteAll()
        session_registry.add_session(
            SessionData('Test Session', self.start_date, self.start_date + timedelta(hours=1), 'os-123'))
        self.fixture_image = Path('tests').joinpath('fixtures/test-image.png')

    def test_add_os_session_image(self):
        response = self.provide_testfile()

        self.assertEqual(201, response.status_code, response.content)
        self.assertEqual(self.test_id, response.json()['identifier'], response.json())
        self.assertEqual(self.test_id, response.json()['session_identifier'], response.json())

    def test_add_os_session_image_to_non_existing_session(self):
        with open(self.fixture_image, 'rb') as image_file:
            response = self.test_client.post('/os/os-123/s/non-existing/i', files={'image': image_file})

        self.assertEqual(404, response.status_code, response.content)

    def test_get_os_session_images(self):
        self.provide_testfile()

        get_response = self.test_client.get(f'/os/os-123/s/{self.test_id}/i')
        self.assertEqual(200, get_response.status_code, get_response.content)
        self.assertEqual(1, len(get_response.json()), get_response.json())
        self.assertDictEqual({
            'identifier': '345',
            'os_identifier': 'os-123',
            'is_header': False,
            'session_identifier': '345'
        }, get_response.json()[0], get_response.json())

    def test_get_os_session_image(self):
        self.provide_testfile()

        get_response = self.test_client.get(f'/os/os-123/s/{self.test_id}/i/345')
        self.assertEqual(200, get_response.status_code, get_response.content)

    def test_get_non_existing_os_session_image(self):
        self.provide_testfile()

        get_response = self.test_client.get(f'/os/os-123/s/{self.test_id}/i/non-345-existing')
        self.assertEqual(404, get_response.status_code, get_response.content)

    def test_delete_session_image(self):
        self.provide_testfile()
        get_response = self.test_client.get(f'/os/os-123/s/{self.test_id}/i/345')
        self.assertEqual(200, get_response.status_code, get_response.content)

        delete_response = self.test_client.delete(f'/os/os-123/s/{self.test_id}/i/345')
        self.assertEqual(204, delete_response.status_code, delete_response.content)

    def provide_testfile(self):
        with open(self.fixture_image, 'rb') as image_file:
            return self.test_client.post(f'/os/os-123/s/{self.test_id}/i', files={'image': image_file})
