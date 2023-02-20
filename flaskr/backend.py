# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage

class Backend:

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)

    def get_wiki_page(self, name):
        pass

    def get_all_page_names(self):
        blobs = self.storage_client.list_blobs(self.bucket_name)
        for blob in blobs:
            print(blob.name)

    def upload(self, page_name, page):
        blob = self.bucket.blob(page_name)
        with blob.open("w") as f:
            f.write(page)

    def sign_up(self):
        pass

    def sign_in(self):
        pass

    def get_image(self):
        pass

b = Backend("contentwiki")
b.upload("warzone", "page")
b.get_all_page_names()