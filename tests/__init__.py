from pathlib import Path
from unittest import TestCase

from httpx import Response
from starlette.testclient import TestClient

from api.model.id_gen import generatorFactoryInstance
from api.routes import app


class ApiTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.fixture_image = Path('tests').joinpath('fixtures/test-image.png')
        self.test_client = TestClient(app)

    def assert_response(self, response: Response, response_code: int = 200):
        self.assertEqual(response_code, response.status_code, response.content)

    def upload_os_image(self, os_identifier='os-123', i_identifier='i-123'):
        self.test_id = i_identifier
        with open(self.fixture_image, 'rb') as image_file:
            test_client_post = self.test_client.post(f'/os/{os_identifier}/i/', files={'image': image_file})
        self.assert_response(test_client_post, 201)
        return test_client_post

    def upload_session_image(self, os_identifier='os-123', s_identifier='s-123', i_identifier='i-123'):
        generatorFactoryInstance.generator_function = lambda: i_identifier
        with open(self.fixture_image, 'rb') as image_file:
            test_client_post = self.test_client.post(f'/os/{os_identifier}/s/{s_identifier}/i',
                                                     files={'image': image_file})
        self.assert_response(test_client_post, 201)
        return test_client_post
