from flaskr.backend import Backend

# TODO(Project 1): Write tests for Backend methods.
import unittest
from unittest.mock import Mock, MagicMock, mock_open, patch
from .backend import Backend

class TestBackend(unittest.TestCase):
    def setUp(self):
        self.bucket_name = 'test-bucket'
        self.backend = Backend(self.bucket_name)
        self.mock_blob = MagicMock()

    def test_upload(self):
        self.mock_blob.exists.return_value = True
        self.mock_blob.download_as_string.return_value = b'test title'
        self.backend.bucket.blob = MagicMock(return_value=self.mock_blob)
        with patch("builtins.open", mock_open(read_data=b'test title')) as mock_file:
            fake_file = open("fakefile")
            fake_file.content_type = '.txt'
            self.backend.upload('test-game', fake_file)
            assert self.backend.get_wiki_page('test-game') == b'test title'
        mock_file.assert_called_with("fakefile")

    def test_get_wiki_page_exists(self):
        name = 'test-page'
        self.mock_blob.exists.return_value = True
        self.mock_blob.download_as_string.return_value = b'Test content'
        self.backend.bucket.blob = MagicMock(return_value=self.mock_blob)

        result = self.backend.get_wiki_page(name)

        self.assertEqual(result, b'Test content')
        self.backend.bucket.blob.assert_called_once_with(name)
        self.mock_blob.exists.assert_called_once()
    
    def test_get_image(self):
        name = 'test-image'
        mock_blob1 = MagicMock()
        mock_blob1.name = "test1"
        mock_blob2 = MagicMock()
        mock_blob2.name = name
        mock_blob3 = MagicMock()
        mock_blob3.name = "test3"
        mock_blobs = MagicMock()
        mock_blobs.return_value = iter({mock_blob1,mock_blob2,mock_blob3})
        self.backend.storage_client.list_blobs = mock_blobs
        with patch("builtins.open", mock_open(read_data=b'img data')) as mock_file:
            result = self.backend.get_image(name, open(mock_blob2))
            assert 'data:image' in result

if __name__ == 'main':
    unittest.main()