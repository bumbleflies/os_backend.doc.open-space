from unittest import TestCase

from httpx import Response


class ApiTestCase(TestCase):
    def assert_response(self, response: Response, response_code: int = 200):
        self.assertEqual(response_code, response.status_code, response.content)
