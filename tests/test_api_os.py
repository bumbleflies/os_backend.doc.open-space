from datetime import datetime, timedelta

from registry.os import os_registry
from tests import AuthEnabledApiTestCase


class TestOsApi(AuthEnabledApiTestCase):

    def setUp(self) -> None:
        super().setUp()
        os_registry.deleteAll()

        self.start_date = datetime(2023, 3, 4, 5, 6, 7)
        self.test_os = {
            'title': 'test title', 'start_date': self.start_date.isoformat(),
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'location': {'lat': 1, 'lng': 2}}

    def test_get_health(self):
        response = self.test_client.get('/health')
        self.assert_response(response, 200)

    def test_create_os(self):
        response = self.auth_test_client.post('/os', json=self.test_os)

        self.assert_response(response, 201)

        self.assertDictEqual({
            'title': 'test title',
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': response.json()['identifier'],
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
        }, response.json())

    def test_get_all_os(self):
        create_response = self.auth_test_client.post('/os', json=self.test_os)

        response = self.test_client.get('/os')
        self.assert_response(response, 200)

        self.assertEqual(1, len(response.json()))

        self.assertDictEqual({
            'title': 'test title',
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': create_response.json()['identifier'],
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
        }, response.json()[0])

    def test_get_os(self):
        create_response = self.auth_test_client.post('/os', json=self.test_os)
        os_id = create_response.json()['identifier']
        os_response = self.test_client.get(f'/os/{os_id}')
        self.assert_response(os_response, 200)

        self.assertDictEqual({
            'title': 'test title',
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': create_response.json()['identifier'],
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
        }, os_response.json())

    def test_get_not_found(self):
        self.assertEqual(404, self.test_client.get('/os/456-not-existing-456').status_code)

    def test_delete_os(self):
        response = self.auth_test_client.post('/os', json=self.test_os)
        os_id = response.json()['identifier']
        self.auth_test_client.delete(f'/os/{os_id}')

    def test_put_os(self):
        response = self.auth_test_client.post('/os', json=self.test_os)
        os_id = response.json()['identifier']
        test_os_2 = dict(self.test_os)
        test_os_2['title'] = 'new title'

        put_response = self.test_client.put(f'/os/{os_id}', json=test_os_2)

        self.assert_response(put_response, 200)
        self.assertDictEqual({
            'title': 'new title',
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': os_id,
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
        }, put_response.json())

    def test_put_not_found(self):
        self.assertEqual(404, self.test_client.put('/os/456-not-existing-456', json=self.test_os).status_code)

    def test_get_os_with_header_image(self):
        create_response = self.auth_test_client.post('/os', json=self.test_os)
        os_id = create_response.json()['identifier']
        image_id = self.upload_os_image(os_identifier=os_id)
        patch_response = self.test_client.patch(f'/os/{os_id}/i/{image_id}', json={'is_header': True})
        self.assert_response(patch_response, 204)
        os_response = self.test_client.get(f'/os/{os_id}?with_header_images=true')
        self.assert_response(os_response, 200)

        self.assertDictEqual({
            'title': 'test title',
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': os_id,
            'location': {'lat': 1.0, 'lng': 2.0},
            'start_date': self.start_date.isoformat(),
            'header_images': [{'identifier': image_id,
                               'is_header': True,
                               'os_identifier': os_id}]
        }, os_response.json())

    def test_put_os_with_place(self):
        response = self.auth_test_client.post('/os', json=self.test_os)
        os_id = response.json()['identifier']
        test_os_2 = dict(self.test_os)
        test_os_2['location'] = {'lat': 1.0, 'lng': 2.0, 'place': 'test place'}

        put_response = self.test_client.put(f'/os/{os_id}', json=test_os_2)

        self.assert_response(put_response, 200)
        self.assertDictEqual({
            'title': 'test title',
            'end_date': (self.start_date + timedelta(days=1)).isoformat(),
            'identifier': os_id,
            'location': {'lat': 1.0, 'lng': 2.0, 'place': 'test place'},
            'start_date': self.start_date.isoformat(),
        }, put_response.json())
