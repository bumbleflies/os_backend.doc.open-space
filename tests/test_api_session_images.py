from datetime import datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from api.model.id_gen import generatorFactoryInstance
from api.model.session_data import SessionData
from api.routes import app
from registry.session import session_registry
from registry.session_images import session_images_registry
from tests import ApiTestCase


class TestSessionImagesApi(ApiTestCase):

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
        response = self.upload_session_image(s_identifier=self.test_id)

        self.assert_response(response, 201)
        self.assertEqual('i-123', response.json()['identifier'], response.json())
        self.assertEqual(self.test_id, response.json()['session_identifier'], response.json())

    def test_add_os_session_image_to_non_existing_session(self):
        with open(self.fixture_image, 'rb') as image_file:
            response = self.test_client.post('/os/os-123/s/non-existing/i', files={'image': image_file})

        self.assert_response(response, 404)

    def test_get_os_session_images(self):
        self.upload_session_image(s_identifier=self.test_id)

        get_response = self.test_client.get(f'/os/os-123/s/{self.test_id}/i')
        self.assert_response(get_response)
        self.assertEqual(1, len(get_response.json()), get_response.json())
        self.assertDictEqual({
            'identifier': 'i-123',
            'os_identifier': 'os-123',
            'is_header': False,
            'session_identifier': '345'
        }, get_response.json()[0], get_response.json())

    def test_get_os_session_image(self):
        self.upload_session_image(s_identifier=self.test_id)

        get_response = self.test_client.get(f'/os/os-123/s/{self.test_id}/i/i-123')
        self.assert_response(get_response)

    def test_get_non_existing_os_session_image(self):
        self.upload_session_image(s_identifier=self.test_id)

        get_response = self.test_client.get(f'/os/os-123/s/{self.test_id}/i/non-345-existing')
        self.assert_response(get_response, 404)

    def test_delete_session_image(self):
        self.upload_session_image(s_identifier=self.test_id)
        get_response = self.test_client.get(f'/os/os-123/s/{self.test_id}/i/i-123')
        self.assert_response(get_response)

        delete_response = self.test_client.delete(f'/os/os-123/s/{self.test_id}/i/345')
        self.assert_response(delete_response, 204)

    def test_make_header_image(self):
        self.upload_session_image(s_identifier=self.test_id)
        patch_response = self.test_client.patch(f'/os/os-123/s/{self.test_id}/i/i-123', json={'is_header': True})
        self.assert_response(patch_response, 204)

    def test_get_header_image(self):
        self.upload_session_image(s_identifier=self.test_id)
        patch_response = self.test_client.patch(f'/os/os-123/s/{self.test_id}/i/i-123', json={'is_header': True})
        self.assert_response(patch_response, 204)
        response = self.test_client.get(f'/os/os-123/s/{self.test_id}/i/?only_header=True')
        self.assert_response(response)
        self.assertDictEqual({
            'identifier': 'i-123',
            'os_identifier': 'os-123',
            'session_identifier': '345',
            'is_header': True,
        }, response.json()[0], response.json())

    def test_only_one_header_image(self):
        self.upload_session_image(s_identifier=self.test_id, i_identifier='i-123')
        self.upload_session_image(s_identifier=self.test_id, i_identifier='i-345')
        patch_response = self.test_client.patch(f'/os/os-123/s/{self.test_id}/i/i-123', json={'is_header': True})
        self.assert_response(patch_response, 204)
        patch_response = self.test_client.patch(f'/os/os-123/s/{self.test_id}/i/i-345', json={'is_header': True})
        self.assert_response(patch_response, 204)
        response = self.test_client.get(f'/os/os-123/s/{self.test_id}/i?only_header=True')
        self.assert_response(response)
        self.assertEqual(1, len(response.json()), response.json())
