# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import hashlib
client = storage.Client()

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

    #@app.route('/sign_up', methods=['POST','GET'])    
    def sign_up(self, user_name, pwd):
        #if request.method == "POST":
            #name = request.form['name']
            #password = request.form['password']
        name = user_name
        password = pwd
        salt = "5gz"

        # Adding salt at the last of the password
        dataBase_password = password+salt
        # Encoding the password
        hashed_password = hashlib.md5(dataBase_password.encode())
 
        # Printing the Hash
        print(hashed_password.hexdigest())

        bucket = client.bucket('userspasswords')
        blob = bucket.blob(name)
        
        with blob.open("w") as f:
            f.write(f"{hashed_password.hexdigest()}")

    def sign_in(self):
        pass

    def get_image(self):
        pass



b = Backend("contentwiki")
b.upload("warzone", "page")
b.get_all_page_names()
b.sign_up("John","John1234")