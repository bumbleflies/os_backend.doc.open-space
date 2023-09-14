from unittest import TestCase

from starlette.testclient import TestClient

from api.routes import app


class TestLoader(TestCase):

    def test_loader_file_present(self):
        self.test_client = TestClient(app)

        response = self.test_client.get('/loaderio-8754cc1aef698fecab6cfcb2185850fe/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(b'loaderio-8754cc1aef698fecab6cfcb2185850fe', response.content)
