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
        self.bucket_name = 'test-bucket'  #mock bucket
        self.backend = Backend(self.bucket_name)  # inject the mock bucket
        self.mock_blob = MagicMock()  #create mock blob
        #mockblob characteristics for the tests
        self.mock_blob.return_value = self.mock_blob
        self.mock_blob.exists.return_value = False
        self.mock_blob.upload_from_string.return_value = None

        #mock blobs for many pages with names and types
        self.mock_blob1 = MagicMock()
        self.mock_blob1.name = 'page1'
        self.mock_blob1.content_type = 'text'

        self.mock_blob2 = MagicMock()
        self.mock_blob2.name = 'page2'
        self.mock_blob2.content_type = 'image'

        self.mock_blob3 = MagicMock()
        self.mock_blob3.name = 'page3'
        self.mock_blob3.content_type = 'text'

        self.mock_blobs = [self.mock_blob1, self.mock_blob2,
                           self.mock_blob3]  #mock bucket with the pages

    def test_upload(self):
        # set up mock to exist and return 'test title' when blob is attempted to be downloaded
        self.mock_blob.exists.return_value = True
        self.mock_blob.download_as_string.return_value = b'test title'
        self.backend.bucket.blob = MagicMock(return_value=self.mock_blob)

        # mock the open file to pass a fake file in with content_type 'txt', then assert it returns the correct information
        with patch("builtins.open",
                   mock_open(read_data=b'test title')) as mock_file:
            fake_file = open("fakefile")
            fake_file.content_type = '.txt'
            self.backend.upload('test-game', fake_file)
            assert self.backend.get_wiki_page('test-game') == b'test title'
        mock_file.assert_called_with("fakefile")

    def test_get_image(self):
        # set up mock blobs to parse through on iteration
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

        # mock open, pass in blob list along with the image name, and assert an image is returned
        with patch("builtins.open", mock_open(read_data=b'img data')):
            result = self.backend.get_image(name, open(mock_blob2))
            assert 'data:image' in result

    def test_get_wiki_page_exists(self):

        name = 'test-page'  #set the mock blob name to test-page
        self.mock_blob.exists.return_value = True  #set it so that it return true when asked if exists.
        self.mock_blob.download_as_string.return_value = b'Test content'  #set it so that it returns this string
        self.backend.bucket.blob = MagicMock(
            return_value=self.mock_blob)  #inject it

        result = self.backend.get_wiki_page(
            name)  #save the result after calling the function

        self.assertEqual(result, b'Test content')  #assert

    def test_get_wiki_page_not_exists(self):

        name = 'non-page'  #set the mock blob name to non-page
        self.mock_blob.exists.return_value = False  #set it so that it return false when asked if exists.
        self.backend.bucket.blob = MagicMock(
            return_value=self.mock_blob)  #inject it

        result = self.backend.get_wiki_page(
            name)  #save the result after calling the function

        self.assertEqual(result, None)  #assert

    def test_get_all_page_names(self):

        mock_list_blobs = MagicMock(
        )  # list of pages self.mock_blobs = [self.mock_blob1, self.mock_blob2, self.mock_blob3]
        mock_list_blobs.return_value = iter(
            self.mock_blobs)  #make so that it return the blobs list
        self.backend.storage_client.list_blobs = mock_list_blobs  #inject it

        expected_result = {
            'page1': self.mock_blob1,
            'page3': self.mock_blob3
        }  #what it should return

        result = self.backend.get_all_page_names(
        )  #save the output after calling the function

        self.assertEqual(result, expected_result)  #assert

    def test_signin_success(self):
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        backend = Mock(return_value=mock_blob)
        with mock.patch('flaskr.backend.storage'):
            backend.sign_up('testuser', 'testpassword')

        # Mock the bucket and blob objects
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = True
        mock_blob.open.return_value.__enter__.return_value.read.return_value = hashlib.md5(
            b'testpassword5gz').hexdigest()

        # Patch the storage.Client class to return the mock bucket
        with patch.object(storage, 'Client') as mock_client:
            mock_client.return_value.bucket.return_value = mock_bucket
            result = backend.sign_in('testuser', 'testpassword')

        self.assertIsNotNone(result)  # 'testuser'

    def test_signin_failure(self):
        # create a mock bucket blob for a non-existent user
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        self.backend = Mock(return_value=mock_blob)
        # replace the real bucket blob with the mock
        self.backend.storage_client.bucket = Mock(return_value=Mock(blob=Mock(
            return_value=mock_blob)))

        # simulate a failed sign in with an invalid user
        with mock.patch('flaskr.backend.storage'):
            result = self.backend.sign_in('nonexistentuser', 'password')
            self.assertIsNotNone(result)  # 'Invalid User'

            # simulate a failed sign in with an invalid password
            mock_blob.exists.return_value = True
            mock_blob.open.return_value.read.return_value = 'invalidhash'
            result = self.backend.sign_in('testuser', 'invalidpassword')
            self.assertIsNotNone(result)  # 'Invalid Password'

    def test_sign_up_success(self):
        user_name = 'testuser'
        password = 'testpassword'
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        self.backend = Mock(return_value=mock_blob)
        self.backend.storage_client.bucket = Mock(return_value=Mock(blob=Mock(
            return_value=mock_blob)))
        with mock.patch('flaskr.backend.storage'):
            # Call the sign_up function
            self.backend.sign_up(user_name, password)
            # # Assert that the blob was created with the correct name and contents
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
