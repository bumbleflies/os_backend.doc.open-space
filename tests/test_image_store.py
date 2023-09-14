from pathlib import Path
from pathlib import Path
from unittest import IsolatedAsyncioTestCase

from fastapi import UploadFile

from api.model.id_gen import generatorFactoryInstance
from api.model.image_data import PersistentImage
from store.image import ImageStore


class TestImageStore(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        generatorFactoryInstance.generator_function = lambda: 'i-123'
        self.fixture_image = Path('tests').joinpath('fixtures/test-image.png')
        self.image_store = ImageStore()
        self.image_store.delete_all()

    async def test_creates_thumbnail(self):
        with open(self.fixture_image, 'rb') as image_file:
            save_task = await self.image_store.save(UploadFile(image_file), PersistentImage(os_identifier='os-123'))

        await save_task
        self.assertTrue(Path('img').joinpath('os-123').joinpath('i-123').exists())
        self.assertTrue(Path('img').joinpath('os-123').joinpath('i-123.thumb').exists())
