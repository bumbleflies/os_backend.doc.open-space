from os import getenv
from pathlib import Path
from unittest import TestCase

from auth0.authentication import GetToken
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

    def upload_os_image(self, os_identifier) -> str:
        with open(self.fixture_image, 'rb') as image_file:
            test_client_post = self.test_client.post(f'/os/{os_identifier}/i/', files={'image': image_file})
        self.assert_response(test_client_post, 201)
        return test_client_post.json()['identifier']

    def upload_session_image(self, os_identifier='os-123', s_identifier='s-123', i_identifier='i-123'):
        generatorFactoryInstance.generator_function = lambda: i_identifier
        with open(self.fixture_image, 'rb') as image_file:
            test_client_post = self.test_client.post(f'/os/{os_identifier}/s/{s_identifier}/i',
                                                     files={'image': image_file})
        self.assert_response(test_client_post, 201)
        return test_client_post


class AuthEnabledApiTestCase(ApiTestCase):
    auth_headers = {}

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        get_token = GetToken(getenv('OS_AUTH_DOMAIN'), getenv('OS_AUTH_TEST_CLIENT_ID'),
                             client_secret=getenv('OS_AUTH_TEST_CLIENT_SECRET'))
        token = get_token.login(getenv('OS_AUTH_TEST_USER_EMAIL'),
                                getenv('OS_AUTH_TEST_USER_PASSWORD'),
                                realm='Username-Password-Authentication',
                                audience=getenv('OS_AUTH_AUDIENCE'))
        AuthEnabledApiTestCase.auth_headers = {'Authorization': f'Bearer {token["access_token"]}'}

    def setUp(self):
        super().setUp()
        self.auth_test_client = TestClient(app)
        self.auth_test_client.headers = AuthEnabledApiTestCase.auth_headers
