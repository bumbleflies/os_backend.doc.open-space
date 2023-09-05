from datetime import datetime, timedelta
from pathlib import Path
from unittest import TestCase

from fastapi.testclient import TestClient

from api.model.id_gen import generatorFactoryInstance
from api.model.session_data import SessionData
from api.routes import app
from registry.session import session_registry


class TestSessionApi(TestCase):

    def setUp(self) -> None:
        self.test_client = TestClient(app)
        self.start_date = datetime(2023, 3, 4, 5, 6, 7)
        self.test_id = '345'
        generatorFactoryInstance.generator_function = lambda: self.test_id
        session_registry.deleteAll()
        session_registry.add_session(
            SessionData('Test Session', self.start_date, self.start_date + timedelta(hours=1), '123'))
        self.fixture_image = Path('tests').joinpath('fixtures/test-image.png')

    def test_add_os_session_image(self):
        with open(self.fixture_image, 'rb') as image_file:
            response = self.test_client.post(f'/os/123/s/{self.test_id}/i', files={'image': image_file})

        self.assertEqual(201, response.status_code, response.content)
        self.assertEqual(self.test_id, response.json()['identifier'], response.json())
        self.assertEqual(self.test_id, response.json()['session_identifier'], response.json())
