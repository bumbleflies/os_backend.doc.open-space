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

    def test_edit_os_sessions(self):
        create_response = self.test_client.post('/os/123/s/', json=self.test_session)

        self.assertEqual(201, create_response.status_code, create_response.content)
        self.assertDictEqual({**self.test_session,
                              'identifier': '345',
                              'os_identifier': '123'}, create_response.json())

        put_response = self.test_client.put('/os/123/s/345', json={
            'title': 'New Title',
            'start_date': (self.start_date + timedelta(hours=2)).isoformat(),
            'end_date': (self.start_date + timedelta(hours=4)).isoformat()
        })

        self.assertEqual(200, put_response.status_code, put_response.content)
        self.assertDictEqual({'title': 'New Title',
                              'start_date': (self.start_date + timedelta(hours=2)).isoformat(),
                              'end_date': (self.start_date + timedelta(hours=4)).isoformat(),
                              'identifier': '345',
                              'os_identifier': '123'}, put_response.json())

    def test_get_os_session(self):
        create_response = self.test_client.post('/os/123/s/', json=self.test_session)

        self.assertEqual(201, create_response.status_code, create_response.content)

        get_response = self.test_client.get('os/123/s/345')
        self.assertEqual(200, get_response.status_code, get_response.content)

    def test_get_non_existent_session(self):
        get_response = self.test_client.get('os/123/s/non-345-existent')
        self.assertEqual(404, get_response.status_code, get_response.content)

    def test_update_non_existent_session(self):
        put_response = self.test_client.put('/os/123/s/non-345-existent', json={
            'title': 'New Title',
            'start_date': (self.start_date + timedelta(hours=2)).isoformat(),
            'end_date': (self.start_date + timedelta(hours=4)).isoformat()
        })

        self.assertEqual(404, put_response.status_code, put_response.content)
