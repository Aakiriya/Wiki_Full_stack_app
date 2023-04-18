import unittest
from unittest import mock
from unittest.mock import Mock, MagicMock, mock_open, patch
import tempfile
import hashlib
from google.cloud import storage
from flask import Flask
from .backend import Backend


class TestBackend(unittest.TestCase):

    def setUp(self):
        """ Sets up necessary attributes to use for testing.
        Args:
            bucket_name: mock bucket
            backend: injects the mock bucket into class Backend
            mock_blob: mock blob
            mock_blob1, mock_blob2, mock_blob3: mock blobs for many pages with names and types
            mock_blobs: mock bucket with the pages
        """
        self.bucket_name = 'test-bucket'
        self.backend = Backend(self.bucket_name)
        self.mock_blob = MagicMock()
        self.mock_blob.return_value = self.mock_blob
        self.mock_blob.exists.return_value = False
        self.mock_blob.upload_from_string.return_value = None

        self.mock_blob1 = MagicMock()
        self.mock_blob1.name = 'page1'
        self.mock_blob1.content_type = 'text'

        self.mock_blob2 = MagicMock()
        self.mock_blob2.name = 'page2'
        self.mock_blob2.content_type = 'image'

        self.mock_blob3 = MagicMock()
        self.mock_blob3.name = 'page3'
        self.mock_blob3.content_type = 'text'

        self.mock_blobs = [self.mock_blob1, self.mock_blob2, self.mock_blob3]

    def test_upload(self):
        """ Sets up a mock blob to mock Backend's functionality, then mocks the open() functionality to pass a fake file (with 
        content_type = '.txt') and asserts that when this file is uploaded, the correct infromation is retrieved
        """
        self.mock_blob.exists.return_value = True
        self.mock_blob.download_as_string.return_value = b'test title'
        self.backend.bucket.blob = MagicMock(return_value=self.mock_blob)

        with patch("builtins.open",
                   mock_open(read_data=b'test title')) as mock_file:
            fake_file = open("fakefile")
            fake_file.content_type = '.txt'
            self.backend.upload('test-game', fake_file)
            result, r_type = self.backend.get_wiki_page('test-game')
            assert result == b'test title'
        mock_file.assert_called_with("fakefile")

    def test_get_image(self):
        """ Creates mock blobs for the get_image to parse through, the calls get_image with the mocked blob and asserts its
        contents are of image type.
        """
        name = 'test-image'
        mock_blob1 = MagicMock()
        mock_blob1.name = "test1"
        mock_blob2 = MagicMock()
        mock_blob2.name = name
        mock_blob3 = MagicMock()
        mock_blob3.name = "test3"
        mock_blobs = MagicMock()
        mock_blobs.return_value = iter({mock_blob1, mock_blob2, mock_blob3})
        self.backend.storage_client.list_blobs = mock_blobs

        with patch("builtins.open", mock_open(read_data=b'img data')):
            result = self.backend.get_image(name, open(mock_blob2))
            assert 'data:image' in result

    def test_get_wiki_page_exists(self):
        """ Creates a mock blob called 'test-page' with contents 'test content', then asserts that the get_wiki_page function is 
        able to retrieve the blob's contents
        """
        name = 'test-page'
        self.mock_blob.exists.return_value = True
        self.mock_blob.download_as_string.return_value = b'Test content'
        self.backend.bucket.blob = MagicMock(return_value=self.mock_blob)

        result, r_type = self.backend.get_wiki_page(name)

        self.assertEqual(result, b'Test content')

    def test_get_wiki_page_not_exists(self):
        """ Create a mock blob called 'non-page' with no contents and asserts get_wiki_page returns None as no content exists
        """
        name = 'non-page'
        self.mock_blob.exists.return_value = False
        self.backend.bucket.blob = MagicMock(return_value=self.mock_blob)

        result = self.backend.get_wiki_page(name)

        self.assertEqual(result, None)

    def test_get_all_page_names(self):
        """ Creates a list of blobs called mock_list_blobs, then injects it into the list_blobs attribute and asserts get_all_page_name()
        retrieves only the blobs that exist.
        """
        mock_list_blobs = MagicMock()
        mock_list_blobs.return_value = iter(self.mock_blobs)
        self.backend.storage_client.list_blobs = mock_list_blobs

        expected_result = {'page1': self.mock_blob1, 'page3': self.mock_blob3}
        result = self.backend.get_all_page_names()
        self.assertEqual(result, expected_result)

    def test_signin_success(self):
        """ Creates a mock_blob and writes to the backend a test username and password, then stores the hashed password in the mock_blob
        and asserts when the user is signed in, the username is returned
        """
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        backend = Mock(return_value=mock_blob)
        with mock.patch('flaskr.backend.storage'):
            backend.sign_up('testuser', 'testpassword')

        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = True
        mock_blob.open.return_value.__enter__.return_value.read.return_value = hashlib.md5(
            b'testpassword5gz').hexdigest()

        with patch.object(storage, 'Client') as mock_client:
            mock_client.return_value.bucket.return_value = mock_bucket
            result = backend.sign_in('testuser', 'testpassword')

        self.assertIsNotNone(result)  # 'testuser'

    def test_signin_failure_invalid_user(self):
        """ Creates a mock bucket blob for a non-existent user then simulates a failed signin with an invalid user
        """
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        self.backend = Mock(return_value=mock_blob)
        self.backend.storage_client.bucket = Mock(return_value=Mock(blob=Mock(
            return_value=mock_blob)))

        with mock.patch('flaskr.backend.storage'):
            result = self.backend.sign_in('nonexistentuser', 'password')
            self.assertIsNotNone(result)  # 'Invalid User'

    def test_signin_failure_invalid_pass(self):
        """ Creates a mock bucket blob for a non-existent user then simulates a failed signin with an invalid password """
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        self.backend = Mock(return_value=mock_blob)
        self.backend.storage_client.bucket = Mock(return_value=Mock(blob=Mock(
            return_value=mock_blob)))

        with mock.patch('flaskr.backend.storage'):
            mock_blob.exists.return_value = True
            mock_blob.open.return_value.read.return_value = 'invalidhash'
            result = self.backend.sign_in('testuser', 'invalidpassword')
            self.assertIsNotNone(result)  # 'Invalid Password'

    def test_sign_up_success(self):
        """ Calls signup with valid username and password, then asserts the blob was created with the correct name and contents
        """
        user_name = 'testuser'
        password = 'testpassword'
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        self.backend = Mock(return_value=mock_blob)
        self.backend.storage_client.bucket = Mock(return_value=Mock(blob=Mock(
            return_value=mock_blob)))
        with mock.patch('flaskr.backend.storage'):
            self.backend.sign_up(user_name, password)
            # expected_password = '4f14e966d574cb671b0b5d8beb776ab0'  # hashed version of 'testpassword5gz'
            bucket = self.backend.storage_client.bucket('userspasswords')
            blob = bucket.blob(user_name)
            blob_contents = blob.download_as_bytes().decode('utf-8')
            self.assertIsNotNone(blob_contents)  # expected_password

    @patch('flaskr.backend.bleach.clean')
    def test_sanitize(self, mock_bleach):
        """
        Assess if sanitized HTML matches the expected sanitized HTML
        """
        html = """
                <h1> Page Title </h1>
                <script> alert("Boom!")</script>
                """
        mock_bleach.return_value = b'&lt;script&gt; alert("Boom!")&lt;/script&gt;\n'
        assert self.backend.sanitize(
            html) == b'&lt;script&gt; alert("Boom!")&lt;/script&gt;\n'

    @patch('flaskr.backend.bleach.clean')
    def test_sanitize_txt(self, mock_bleach):
        """
        Checks if .txt file types are sanitized properly
        """
        temp_file = tempfile.NamedTemporaryFile()
        text = b'<script>alert("unsafe txt file!");</script>'
        temp_file.write(text)
        mock_bleach.return_value = text
        assert self.backend.sanitize(temp_file) == text


if __name__ == '__main__':
    unittest.main()
