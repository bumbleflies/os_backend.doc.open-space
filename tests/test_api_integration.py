from datetime import datetime, timedelta

from registry.image import image_registry
from registry.image_details import image_details_registry
from registry.os import os_registry
from registry.session import session_registry
from registry.session_images import session_images_registry
from tests import AuthEnabledApiTestCase


class TestIntegrationApi(AuthEnabledApiTestCase):

    def setUp(self) -> None:
        super().setUp()
        os_registry.deleteAll()
        image_registry.deleteAll()
        image_details_registry.deleteAll()
        session_registry.deleteAll()
        session_images_registry.deleteAll()

        self.start_date = datetime(2023, 3, 4, 5, 6, 7)
        self.test_session = {
            'title': 'Test Session',
            'start_date': self.start_date.isoformat(),
            'end_date': (self.start_date + timedelta(hours=1)).isoformat()
        }

    def test_deletes_session_when_os_is_deleted(self):
        os_registry.add_os(self.test_os)
        os_id = self.test_os.identifier

        session_create_response = self.test_client.post(f'/os/{os_id}/s', json=self.test_session)
        self.assert_response(session_create_response, 201)

        session_get_response = self.test_client.get(f'/os/{os_id}/s')
        self.assert_response(session_get_response, 200)
        self.assertEqual(1, len(session_get_response.json()))

        os_delete_response = self.test_client.delete(f'/os/{os_id}')
        self.assert_response(os_delete_response, 204)

        session_get_response = self.test_client.get(f'/os/{os_id}/s')
        self.assert_response(session_get_response, 200)
        self.assertEqual(0, len(session_get_response.json()))

