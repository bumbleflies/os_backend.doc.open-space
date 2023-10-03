from datetime import timedelta

from registry.os import os_registry
from tests import AuthEnabledApiTestCase


class TestOsApi(AuthEnabledApiTestCase):

    def setUp(self) -> None:
        super().setUp()
        os_registry.deleteAll()

    def test_get_health(self):
        response = self.test_client.get('/health')
        self.assert_response(response, 200)

    def test_create_os(self):
        response = self.auth_test_client.post('/os', json=self.test_os_json)

        self.assert_response(response, 201)

        self.assertDictEqual({
            'title': 'Test Open Space',
            'owner': self.user_id,
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': response.json()['identifier'],
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
        }, response.json())

    def test_get_all_os(self):
        os_registry.add_os(self.test_os)

        response = self.test_client.get('/os')
        self.assert_response(response, 200)

        self.assertEqual(1, len(response.json()))

        self.assertDictEqual({
            'title': 'Test Open Space',
            'owner': self.user_id,
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': self.test_os.identifier,
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
        }, response.json()[0])

    def test_get_os(self):
        os_registry.add_os(self.test_os)
        os_response = self.test_client.get(f'/os/{self.test_os.identifier}')
        self.assert_response(os_response, 200)

        self.assertDictEqual({
            'title': 'Test Open Space',
            'owner': self.user_id,
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': self.test_os.identifier,
            'location': {'lat': 1, 'lng': 2},
            'start_date': self.start_date.isoformat(),
        }, os_response.json())

    def test_get_not_found(self):
        self.assertEqual(404, self.test_client.get('/os/456-not-existing-456').status_code)

    def test_delete_os(self):
        os_registry.add_os(self.test_os)
        response = self.auth_test_client.delete(f'/os/{self.test_os.identifier}')
        self.assert_response(response, 204)

    def test_put_os(self):
        os_registry.add_os(self.test_os)
        test_os_2 = dict(self.test_os_json)
        test_os_2['title'] = 'new title'

        put_response = self.auth_test_client.put(f'/os/{self.test_os.identifier}', json=test_os_2)

        self.assert_response(put_response, 200)
        self.assertDictEqual({
            'title': 'new title',
            'owner': self.user_id,
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': self.test_os.identifier,
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
        }, put_response.json())

    def test_put_not_found(self):
        self.assertEqual(403, self.auth_test_client.put('/os/456-not-existing-456', json=self.test_os_json).status_code)

    def test_get_os_with_header_image(self):
        os_registry.add_os(self.test_os)
        image_id = self.upload_os_image(os_identifier=self.test_os.identifier)
        patch_response = self.test_client.patch(f'/os/{self.test_os.identifier}/i/{image_id}', json={'is_header': True})
        self.assert_response(patch_response, 204)
        os_response = self.test_client.get(f'/os/{self.test_os.identifier}?with_header_images=true')
        self.assert_response(os_response, 200)

        self.assertDictEqual({
            'title': 'Test Open Space',
            'owner': self.user_id,
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': self.test_os.identifier,
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
            'header_images': [{'identifier': image_id,
                               'is_header': True,
                               'owner': self.user_id,
                               'os_identifier': self.test_os.identifier}]
        }, os_response.json())

    def test_put_os_with_place(self):
        os_registry.add_os(self.test_os)
        test_os_2 = dict(self.test_os_json)
        test_os_2['location'] = {'lat': 1.0, 'lng': 2.0, 'place': 'test place'}

        put_response = self.auth_test_client.put(f'/os/{self.test_os.identifier}', json=test_os_2)

        self.assert_response(put_response, 200)
        self.assertDictEqual({
            'title': 'Test Open Space',
            'owner': self.user_id,
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': self.test_os.identifier,
            'location': {'lat': 1.0, 'lng': 2.0, 'place': 'test place'},
            'start_date': self.start_date.isoformat(),
        }, put_response.json())
