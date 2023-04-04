# TODO(Project 1): Implement Backend according to the requirements.
from flask import Blueprint, request, Flask, render_template, session
from flask import request, Flask
from google.cloud import storage
import hashlib
from io import BytesIO
import urllib, base64
import requests

client = storage.Client()


class Backend:
    """
    Class Backend holds the methods to interact with Google Cloud Storage(GCS) and external dependencies such as APIs.
    The methods within this class are called within pages.py, which hold the routes throughout the web application.

    Attributes:
        bucket_name: A string that represents the name of the bucket stored in GCS
        storage_client: A instance of the object Storage representing the storage client
        bucket: A instance of the object Bucket that holds the bucket correlating to the supplied bucket_name
    """

    def __init__(self, bucket_name):
        """Initializes the instance of backend based on the bucket_name supplied

        Args:
          bucket_name: name of the bucket in which the user wants to access
        """
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)

    def get_wiki_page(self, name):
        """ Fetches the wiki contents based on the page name Strings will be UTF-8 encoded and thus will need to be 
        decoded later.
        Args:
            name: String representing the name of the wiki page
        Returns:
            String contents of the current page if the page exists, if not, returns None
        """
        blob = self.bucket.blob(name)
        if blob.exists():
            return blob.download_as_string()
        else:
            return None

    def get_all_page_names(self):
        """ Retrives all of the blob objects of the current bucket by using the storage_client attribute to list the blobs,
        then iterating through each blob and - if the blob is not type "image" - storing the blob in a dictionary to return
        Args: None
        Returns:
            Dictionary where key = blob-name (String), value = Blob (Blob object)
        """
        blobs = self.storage_client.list_blobs(self.bucket_name)
        pages = {}
        for blob in blobs:
            if blob.content_type != 'image':
                pages[blob.name] = blob
        return pages

    def upload(self, page_name, page):
        """ Uploads the supplied page by retrieving the blob in the bucket that matches the supplied page_name (or creates
        the blob if it does not exist). Adds an "image" tag to the blob if the file is type "jpeg", "jpg" or "png", and then
        writes the page to the blob in cloud.
        Args:
            page-name: String representing the name of the wikipage
            page: File object containing the contents of the wiki page
        Returns:
            String contents of the current page if the page exists, if not, returns None
        """
        blob = self.bucket.blob(page_name)
        img = ["image/jpeg", "image/jpg", "image/png"]
        if page.content_type in img:
            blob.content_type = "image"
        with blob.open("wb") as f:
            f.write(page.read())

    def get_genre(self, title):
        """ Uses the IGDB API to find valid genres for the supplied title name. First uses the /games endpoint to find a matching
        title based on data where name equals the supplied title. Next, if a title is found, checks to see if genres are associated
        to that title, and if so, uses the /genres endpoint to translate the genre ID to human-readable genre categories (eg. "Sports")
        and appends each genre to a list to return
        Args:
            title: String representing the name of the game to find genres for
        Returns:
            - List of valid genres if a title is found and genres are found for the title
            - "Title not found" if API does not find the title
            - "Could not find genres for title" if title is found but genres are not currently supplied for genre in database
        """
        headers = {
            "Client-ID": "lgizwf7xy2tobsd42vbrmna4pgot14",
            "Authorization": "Bearer rzqcmetxt2td6c5rvuhiq6ytdlc14d"
        }
        data = f'fields *; where name = "{title}";'
        r = requests.post("https://api.igdb.com/v4/games/",
                          headers=headers,
                          data=data).json()
        game_genres = []
        if len(r) > 0:
            try:
                genres = r[0]['genres']
                for genre in genres:
                    data = f'fields *; where id = {genre};'
                    r = requests.post("https://api.igdb.com/v4/genres/",
                                      headers=headers,
                                      data=data).json()
                    game_genres.append(r[0]['name'])
                return game_genres
            except KeyError:
                return "Could not find genres for title."
        return "Title not found."

    def upload_genre(self, genre, title):
        """ Uploads the title to its correlating genre in the cloud by retrieving the genre blob content that correlates to the genre name,
        appending the title name (if there are current titles, else adds the title to content) and writing the content back to the cloud
        Args:
            genre: String representing the genre name
            title: String representing the game name
        Returns: None
        """
        blob = self.bucket.blob(genre)
        current_blob_content = self.get_wiki_page(genre)
        if not current_blob_content:
            current_blob_content = title.encode('utf-8')
        else:
            current_blob_content = current_blob_content + (
                "," + title).encode('utf-8')
        with blob.open("wb") as f:
            f.write(current_blob_content)

    def sign_up(self, user_name, pwd):
        """ Adds the salt to the end of the supplied password and encodes it using MD5 encryption. Retrieves the bucket containing
        all passwords and creates a blob where the title of the blob is the username, and the blob contents is the encrypted password
        Args:
            user_name: String representing the username of current user
            pwd: String representing the password of current user
        Returns: None
        """
        name = user_name
        password = pwd
        salt = "5gz"

        dataBase_password = password + salt
        hashed_password = hashlib.md5(dataBase_password.encode())

        bucket = client.bucket('userspasswords')
        blob = bucket.blob(name)

        with blob.open("w") as f:
            f.write(f"{hashed_password.hexdigest()}")

    def sign_in(self, user_name, pwd):
        """ Retrieves the username and password for the user and encodes the supplied password combined with the salt. Then retrieves
        the Bucket storing all usernames and the blob correlating to the username the user supplies. If the encrypted passwords match,
        returns the username.
        Args:
            user_name: String representing the username of current user
            pwd: String representing the password of current user
        Returns:
            - String representing the username of the user if the user is valid
            - 'Invalid User' if the user is not found in the bucket
            - 'Invalid Password' if the password supplied does not match the password found in the bucket
        """
        username = user_name
        password = pwd
        salt = "5gz"

        dataBase_password = password + salt
        hashed_password = hashlib.md5(dataBase_password.encode())

        bucket = client.bucket('userspasswords')
        blob = bucket.blob(username)

        if not blob.exists():
            return 'Invalid User'
        else:
            with blob.open("r") as f:
                psw = f.read()
            if hashed_password.hexdigest() != psw:
                return 'Invalid Password'
            else:
                return username

    def get_image(self, image_name, blob_param=None):
        """ Retrieves the image matching the image name supplied by the user by finding the Blob that matches the image name and
        decoding the image to readable version to display on html page
        Args:
           image_name = String representing name of the Blob
        Returns:
           Image object with the correlating image
        """
        blobs = self.storage_client.list_blobs(self.bucket_name)

        def decode_img(image):
            img_string = base64.b64encode(image.read())
            img = 'data:image/png;base64,' + urllib.parse.quote(img_string)
            return img

        if blob_param:
            return decode_img(blob_param)

        for blob in blobs:
            if blob.name == image_name:
                with blob.open("rb") as b:
                    return decode_img(b)
