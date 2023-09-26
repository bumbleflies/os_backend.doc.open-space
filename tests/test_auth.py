from os import getenv

from tests import AuthEnabledApiTestCase


class TestAuthentication(AuthEnabledApiTestCase):

    def test_make_authenticated_call(self):
        self.assertIsNotNone(getenv('OS_AUTH_DOMAIN'))
        self.assertIsNotNone(getenv('OS_AUTH_TEST_CLIENT_ID'))
        self.assertIsNotNone(getenv('OS_AUTH_TEST_CLIENT_SECRET'))

        response = self.auth_test_client.get('/auth')
        self.assertEqual(200, response.status_code, response.content)

        self.assertIn('permissions', response.json())
        self.assertIn('create:os', response.json()['permissions'], response.content)
