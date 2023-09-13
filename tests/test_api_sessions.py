from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from api.model.id_gen import generatorFactoryInstance
from api.routes import app
from registry.session import session_registry
from registry.session_images import session_images_registry
from tests import ApiTestCase


class TestSessionApi(ApiTestCase):

    def setUp(self) -> None:
        super().setUp()
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
        session_images_registry.deleteAll()

    def test_add_os_session(self):
        response = self.test_client.post('/os/123/s/', json=self.test_session)

        self.assert_response(response, 201)
        self.assertEqual('345', response.json()['identifier'], response.json())
        self.assertEqual('123', response.json()['os_identifier'], response.json())
        self.assertEqual(1, len(session_registry.getByQuery({'identifier': '345'})), 'only one session per identifier')

    def test_get_os_sessions(self):
        self.test_client.post('/os/123/s/', json=self.test_session)

        response = self.test_client.get('/os/123/s/')
        self.assert_response(response, 200)
        self.assertEqual(1, len(response.json()))

    def test_edit_os_sessions(self):
        create_response = self.test_client.post('/os/123/s/', json=self.test_session)

        self.assert_response(create_response, 201)
        self.assertDictEqual({**self.test_session,
                              'identifier': '345',
                              'os_identifier': '123'}, create_response.json())

        put_response = self.test_client.put('/os/123/s/345', json={
            'title': 'New Title',
            'start_date': (self.start_date + timedelta(hours=2)).isoformat(),
            'end_date': (self.start_date + timedelta(hours=4)).isoformat()
        })

        self.assert_response(put_response, 200)
        self.assertDictEqual({'title': 'New Title',
                              'start_date': (self.start_date + timedelta(hours=2)).isoformat(),
                              'end_date': (self.start_date + timedelta(hours=4)).isoformat(),
                              'identifier': '345',
                              'os_identifier': '123'}, put_response.json())

    def test_get_os_session(self):
        create_response = self.test_client.post('/os/123/s/', json=self.test_session)
        self.assert_response(create_response, 201)

        get_response = self.test_client.get('os/123/s/345')
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
        create_response = self.test_client.post('/os/123/s/', json=self.test_session)
        self.assert_response(create_response, 201)

        delete_response = self.test_client.delete('/os/123/s/345')
        self.assert_response(delete_response, 204)

    def test_get_session_with_header_images(self):
        create_response = self.test_client.post('/os/123/s/', json=self.test_session)
        self.assert_response(create_response, 201)
        upload_response = self.upload_session_image(s_identifier=self.test_id, os_identifier='123')
        self.assert_response(upload_response, 201)
        patch_response = self.test_client.patch(f'/os/123/s/{self.test_id}/i/{upload_response.json()["identifier"]}',
                                                json={'is_header': True})
        self.assert_response(patch_response, 204)

        get_response = self.test_client.get('os/123/s?with_header_images=true')
        self.assert_response(get_response, 200)

        self.assertDictEqual({'end_date': (self.start_date + timedelta(hours=1)).isoformat(),
                              'identifier': '345',
                              'os_identifier': '123',
                              'start_date': self.start_date.isoformat(),
                              'title': 'Test Session',
                              'header_images': [{'identifier': upload_response.json()["identifier"],
                                                 'is_header': True,
                                                 'os_identifier': '123',
                                                 'session_identifier': '345'}]
                              }, get_response.json()[0])
