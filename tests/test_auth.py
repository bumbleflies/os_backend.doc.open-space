from os import getenv
from unittest import TestCase

from auth0.authentication import GetToken
from starlette.testclient import TestClient

from api.routes import app


def get_authorization_header():
    get_token = GetToken(getenv('OS_AUTH_DOMAIN'), getenv('OS_AUTH_TEST_CLIENT_ID'),
                         client_secret=getenv('OS_AUTH_TEST_CLIENT_SECRET'))
    token = get_token.login(getenv('OS_AUTH_TEST_USER_EMAIL'), getenv('OS_AUTH_TEST_USER_PASSWORD'),
                            realm='Username-Password-Authentication', audience=getenv('OS_AUTH_AUDIENCE'))
    return {'Authorization': f'Bearer {token["access_token"]}'}


class TestAuthentication(TestCase):

    def test_make_authenticated_call(self):
        self.test_client = TestClient(app)

        response = self.test_client.get('/auth', headers=get_authorization_header())
        self.assertEqual(200, response.status_code, response.content)

        self.assertIn('permissions', response.json())
        self.assertIn('create:os', response.json()['permissions'], response.content)
