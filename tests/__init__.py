from dataclasses import asdict
from datetime import datetime, timedelta
from os import getenv
from pathlib import Path
from unittest import TestCase

from auth0.authentication import GetToken
from httpx import Response
from starlette.testclient import TestClient

from api.model.id_gen import generatorFactoryInstance
from api.model.os_data import Location, PersistentOpenSpaceData
from api.model.session_data import SessionData
from api.routes import app


class ApiTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.fixture_image = Path('tests').joinpath('fixtures/test-image.png')
        self.test_client = TestClient(app)
        self.start_date = datetime(2023, 3, 4, 5, 6, 7)

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
        if not cls.auth_headers:
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
        self.user_id = 'auth0|6512a35cce390cfd180872fb'
        self.test_os = PersistentOpenSpaceData('Test Open Space', self.start_date,
                                               self.start_date + timedelta(days=1), Location(1.0, 2.0),
                                               self.user_id)
        self.test_os_json = asdict(self.test_os)
        self.test_os_json['start_date'] = self.test_os_json['start_date'].isoformat()
        self.test_os_json['end_date'] = self.test_os_json['end_date'].isoformat()

        self.test_id = '345'
        self.test_session = SessionData(title='Test Session', start_date=self.start_date,
                                        end_date=self.start_date + timedelta(hours=1), os_identifier=self.test_id,
                                        owner=self.user_id)
        self.test_session_json = asdict(self.test_session)
        self.test_session_json['start_date'] = self.test_session_json['start_date'].isoformat()
        self.test_session_json['end_date'] = self.test_session_json['end_date'].isoformat()

    def upload_os_image(self, os_identifier) -> str:
        with open(self.fixture_image, 'rb') as image_file:
            test_client_post = self.auth_test_client.post(f'/os/{os_identifier}/i/', files={'image': image_file})
        self.assert_response(test_client_post, 201)
        return test_client_post.json()['identifier']

    def upload_session_image(self, os_identifier='os-123', s_identifier='s-123', i_identifier='i-123'):
        generatorFactoryInstance.generator_function = lambda: i_identifier
        with open(self.fixture_image, 'rb') as image_file:
            test_client_post = self.auth_test_client.post(f'/os/{os_identifier}/s/{s_identifier}/i',
                                                          files={'image': image_file})
        self.assert_response(test_client_post, 201)
        return test_client_post
