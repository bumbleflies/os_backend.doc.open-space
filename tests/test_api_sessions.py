from datetime import datetime, timedelta
from unittest import TestCase

from fastapi.testclient import TestClient

from api.model.id_gen import generatorFactoryInstance
from api.routes import app
from registry.session import session_registry


class TestSessionApi(TestCase):

    def setUp(self) -> None:
        self.test_client = TestClient(app)
        self.start_date = datetime(2023, 3, 4, 5, 6, 7)
        self.test_id = '345'
        generatorFactoryInstance.generator_function = lambda: self.test_id
        self.test_session = {
            'title': 'Test Session',
            'start_date': self.start_date.isoformat(),
            'end_date': (self.start_date + timedelta(hours=1)).isoformat()
        }
        session_registry.deleteAll()

    def test_add_os_session(self):
        response = self.test_client.post('/os/123/s/', json=self.test_session)

        self.assertEqual(201, response.status_code, response.content)
        self.assertEqual('345', response.json()['identifier'], response.json())
        self.assertEqual('123', response.json()['os_identifier'], response.json())
        self.assertEqual(1, len(session_registry.getByQuery({'identifier': '345'})), 'only one session per identifier')

    def test_get_os_sessions(self):
        self.test_client.post('/os/123/s/', json=self.test_session)

        response = self.test_client.get('/os/123/s/')
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual(1, len(response.json()))
