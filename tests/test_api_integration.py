from datetime import datetime, timedelta
from unittest import TestCase

from starlette.testclient import TestClient

from api.routes import app
from registry.image import image_registry
from registry.image_details import image_details_registry
from registry.os import os_registry
from registry.session import session_registry
from registry.session_images import session_images_registry


class TestIntegrationApi(TestCase):

    def setUp(self) -> None:
        self.test_client = TestClient(app)
        os_registry.deleteAll()
        image_registry.deleteAll()
        image_details_registry.deleteAll()
        session_registry.deleteAll()
        session_images_registry.deleteAll()

        self.start_date = datetime(2023, 3, 4, 5, 6, 7)
        self.test_os = {
            'title': 'test title', 'start_date': self.start_date.isoformat(),
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'location': {'lat': 1, 'lng': 2}}
        self.test_session = {
            'title': 'Test Session',
            'start_date': self.start_date.isoformat(),
            'end_date': (self.start_date + timedelta(hours=1)).isoformat()
        }

    def test_deletes_session_when_os_is_deleted(self):
        os_create_response = self.test_client.post('/os/', json=self.test_os)
        self.assertEqual(201, os_create_response.status_code, os_create_response.content)

        os_id = os_create_response.json()['identifier']

        session_create_response = self.test_client.post(f'/os/{os_id}/s', json=self.test_session)
        self.assertEqual(201, session_create_response.status_code, session_create_response.content)

        session_get_response = self.test_client.get(f'/os/{os_id}/s')
        self.assertEqual(200, session_get_response.status_code, session_get_response.content)
        self.assertEqual(1, len(session_get_response.json()))

        os_delete_response = self.test_client.delete(f'/os/{os_id}')
        self.assertEqual(204, os_delete_response.status_code, os_delete_response.content)

        session_get_response = self.test_client.get(f'/os/{os_id}/s')
        self.assertEqual(200, session_get_response.status_code, session_get_response.content)
        self.assertEqual(0, len(session_get_response.json()))
