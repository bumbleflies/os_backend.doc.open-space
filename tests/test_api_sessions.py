from dataclasses import asdict
from datetime import datetime, timedelta

from api.model.session_data import SessionData
from registry.session import session_registry
from registry.session_images import session_images_registry
from tests import AuthEnabledApiTestCase


class TestSessionApi(AuthEnabledApiTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.start_date = datetime(2023, 3, 4, 5, 6, 7)
        self.test_id = '345'
        self.test_session = SessionData(title='Test Session', start_date=self.start_date,
                                        end_date=self.start_date + timedelta(hours=1), os_identifier=self.test_id,
                                        owner=self.user_id)
        self.test_session_json = asdict(self.test_session)
        self.test_session_json['start_date'] = self.test_session_json['start_date'].isoformat()
        self.test_session_json['end_date'] = self.test_session_json['end_date'].isoformat()

        session_registry.deleteAll()
        session_images_registry.deleteAll()
        session_registry.add_session(self.test_session)

    def test_add_os_session(self):
        response = self.auth_test_client.post('/os/123/s/', json=self.test_session_json)

        self.assert_response(response, 201)
        self.assertEqual('123', response.json()['os_identifier'], response.json())
        self.assertEqual(1, len(session_registry.getByQuery({'identifier': response.json()['identifier']})),
                         'only one session per identifier')

    def test_get_os_sessions(self):
        session_registry.add_session(self.test_session)

        response = self.test_client.get(f'/os/{self.test_session.os_identifier}/s/')
        self.assert_response(response, 200)
        self.assertEqual(1, len(response.json()))

    def test_edit_os_sessions(self):
        session_registry.add_session(self.test_session)

        put_response = self.test_client.put(f'/os/{self.test_session.os_identifier}/s/{self.test_session.identifier}',
                                            json={
                                                'title': 'New Title',
                                                'start_date': (self.start_date + timedelta(hours=2)).isoformat(),
                                                'end_date': (self.start_date + timedelta(hours=4)).isoformat()
                                            })

        self.assert_response(put_response, 200)
        self.assertDictEqual({'title': 'New Title',
                              'owner': self.user_id,
                              'start_date': (self.start_date + timedelta(hours=2)).isoformat(),
                              'end_date': (self.start_date + timedelta(hours=4)).isoformat(),
                              'identifier': self.test_session.identifier,
                              'os_identifier': self.test_session.os_identifier}, put_response.json())

    def test_get_os_session(self):
        session_registry.add_session(self.test_session)

        get_response = self.test_client.get(f'/os/{self.test_session.os_identifier}/s/{self.test_session.identifier}')
        self.assert_response(get_response, 200)

    def test_get_non_existent_session(self):
        get_response = self.test_client.get('os/123/s/non-345-existent')
        self.assert_response(get_response, 404)

    def test_update_non_existent_session(self):
        put_response = self.test_client.put('/os/123/s/non-345-existent', json={
            'title': 'New Title',
            'start_date': (self.start_date + timedelta(hours=2)).isoformat(),
            'end_date': (self.start_date + timedelta(hours=4)).isoformat()
        })

        self.assert_response(put_response, 404)

    def test_delete_session(self):
        session_registry.add_session(self.test_session)

        delete_response = self.auth_test_client.delete(
            f'/os/{self.test_session.os_identifier}/s/{self.test_session.identifier}')
        self.assert_response(delete_response, 204)

    def test_get_session_with_header_images(self):
        session_registry.add_session(self.test_session)
        upload_response = self.upload_session_image(s_identifier=self.test_session.identifier,
                                                    os_identifier=self.test_session.os_identifier)
        self.assert_response(upload_response, 201)
        patch_response = self.test_client.patch(
            f'/os/{self.test_session.os_identifier}/s/{self.test_session.identifier}/i/{upload_response.json()["identifier"]}',
            json={'is_header': True})
        self.assert_response(patch_response, 204)

        get_response = self.test_client.get(f'os/{self.test_session.os_identifier}/s?with_header_images=true')
        self.assert_response(get_response, 200)

        self.assertDictEqual({'end_date': (self.start_date + timedelta(hours=1)).isoformat(),
                              'identifier': self.test_session.identifier,
                              'os_identifier': self.test_session.os_identifier,
                              'owner': self.user_id,
                              'start_date': self.start_date.isoformat(),
                              'title': 'Test Session',
                              'header_images': [{'identifier': upload_response.json()["identifier"],
                                                 'is_header': True,
                                                 'os_identifier': self.test_session.os_identifier,
                                                 'session_identifier': self.test_session.identifier}]
                              }, get_response.json()[0])
