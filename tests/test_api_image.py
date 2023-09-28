import uuid
from io import BytesIO
from os import listdir
from pathlib import Path

from PIL import Image
from httpx import Response

from api.model.image_data import ImageType, image_type_sizes
from registry.image import image_registry
from store.image import image_storage
from tests import ApiTestCase


class TestImageApi(ApiTestCase):

    def setUp(self) -> None:
        super().setUp()
        image_registry.deleteAll()
        image_storage.delete_all()
        self.test_id = str(uuid.uuid4())

    def test_create_os_image(self):
        with open(self.fixture_image, 'rb') as image_file:
            response = self.test_client.post(f'/os/{self.test_id}/i/', files={'image': image_file})

        self.assert_response(response, 201)
        self.assertEqual(self.test_id, response.json()['os_identifier'], response.json())

    def test_get_os_image(self):
        image_id = self.upload_os_image(self.test_id)
        response = self.test_client.get(f'/os/{self.test_id}/i/{image_id}')
        self.assert_response(response, 200)

    def test_get_os_images(self):
        image_id = self.upload_os_image(self.test_id)
        response = self.test_client.get(f'/os/{self.test_id}/i/')
        self.assert_response(response, 200)
        self.assertEqual(1, len(response.json()), response.json())
        self.assertDictEqual({
            'identifier': image_id,
            'os_identifier': self.test_id,
            'is_header': True,
        }, response.json()[0], response.json())

    def test_delete_os_image(self):
        image_id = self.upload_os_image(self.test_id)
        response = self.test_client.delete(f'/os/{self.test_id}/i/{image_id}')
        self.assert_response(response, 204)

    def test_make_header(self):
        image_id = self.upload_os_image(self.test_id)
        patch_response = self.test_client.patch(f'/os/{self.test_id}/i/{image_id}', json={'is_header': True})
        self.assert_response(patch_response, 204)
        response = self.test_client.get(f'/os/{self.test_id}/i/')
        self.assert_response(response, 200)
        self.assertDictEqual({
            'identifier': image_id,
            'os_identifier': self.test_id,
            'is_header': True,
        }, response.json()[0], response.json())

    def test_get_header_image(self):
        image_id = self.upload_os_image(self.test_id)
        patch_response = self.test_client.patch(f'/os/{self.test_id}/i/{image_id}', json={'is_header': True})
        self.assert_response(patch_response, 204)
        response = self.test_client.get(f'/os/{self.test_id}/i/?only_header=True')
        self.assert_response(response, 200)
        self.assertDictEqual({
            'identifier': image_id,
            'os_identifier': self.test_id,
            'is_header': True,
        }, response.json()[0], response.json())

    def test_only_one_header_image(self):
        image_id1 = self.upload_os_image(self.test_id)
        image_id2 = self.upload_os_image(self.test_id)
        self.assertTrue(image_id1 != image_id2)
        self.assertEqual(204, self.test_client.patch(f'/os/{self.test_id}/i/{image_id1}',
                                                     json={'is_header': True}).status_code)
        self.assertEqual(204, self.test_client.patch(f'/os/{self.test_id}/i/{image_id2}',
                                                     json={'is_header': True}).status_code)
        response = self.test_client.get(f'/os/{self.test_id}/i/?only_header=True')
        self.assert_response(response, 200)
        self.assertEqual(1, len(response.json()), response.json())

    def test_first_impression_becomes_header(self):
        image_id = self.upload_os_image(self.test_os.identifier)
        response = self.test_client.get(f'/os/{self.test_os.identifier}/i/?only_header=True')
        self.assert_response(response, 200)
        self.assertEqual(1, len(response.json()), response.json())
        self.assertDictEqual({
            'identifier': image_id,
            'os_identifier': self.test_os.identifier,
            'is_header': True,
        }, response.json()[0], response.json())

    def test_image_dir_is_deleted_when_empty(self):
        with open(self.fixture_image, 'rb') as image_file:
            response1 = self.test_client.post(f'/os/{self.test_id}/i/', files={'image': image_file})
            response2 = self.test_client.post(f'/os/{self.test_id}/i/', files={'image': image_file})
            self.assert_response(response1, 201)
            self.assert_response(response2, 201)

        response = self.test_client.get(f'/os/{self.test_id}/i/')
        self.assert_response(response, 200)
        self.assertEqual(2, len(response.json()), response.json())
        self.assertEqual(6, len(listdir(Path('img').joinpath(self.test_id))))
        response_del1 = self.test_client.delete(f'/os/{self.test_id}/i/{response1.json()["identifier"]}')
        self.assert_response(response_del1, 204)
        response_del2 = self.test_client.delete(f'/os/{self.test_id}/i/{response2.json()["identifier"]}')
        self.assert_response(response_del2, 204)
        self.assertFalse(Path('img').joinpath(self.test_id).exists())

    def test_get_image_different_sizes(self):
        image_id = self.upload_os_image(self.test_id)
        response = self.test_client.get(f'/os/{self.test_id}/i/{image_id}?image_type=thumb')
        self.assert_image_type(response, image_type_sizes[ImageType.thumb])
        response = self.test_client.get(f'/os/{self.test_id}/i/{image_id}?image_type=header')
        self.assert_image_type(response, image_type_sizes[ImageType.header])
        response = self.test_client.get(f'/os/{self.test_id}/i/{image_id}?image_type=full')
        self.assert_image_type(response, (301, 301))
        response = self.test_client.get(f'/os/{self.test_id}/i/{image_id}')
        self.assert_image_type(response, (301, 301))

    def assert_image_type(self, response: Response, size: tuple[int, int]):
        self.assert_response(response, 200)
        with Image.open(BytesIO(response.content)) as image:
            self.assertEqual('PNG', image.format)
            self.assertEqual(size, image.size)
