# TODO(Project 1): Implement Backend according to the requirements.
from flask import Blueprint,request, Flask, render_template
from google.cloud import storage
import hashlib
from io import BytesIO
import urllib, base64

client = storage.Client()
app = Flask(__name__)

@app.route('/')
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
        img = ["image/jpeg", "image/jpg", "image/png"]
        if page.content_type in img:
            blob.content_type = "image"
        with blob.open("wb") as f:
            f.write(page.read())
 
    def sign_up(self,user_name, pwd):        
        name = user_name
        password = pwd
        salt = "5gz"

        # Adding salt at the last of the password
        dataBase_password = password+salt
        # Encoding the password
        hashed_password = hashlib.md5(dataBase_password.encode())
    
        bucket = client.bucket('userspasswords')
        blob = bucket.blob(name)
            
        with blob.open("w") as f:
            f.write(f"{hashed_password.hexdigest()}")


    def sign_in(self,user_name, pwd):        
        username = user_name
        password = pwd
        salt = "5gz"

        # Adding salt at the last of the password
        dataBase_password = password+salt
        # Encoding the password
        hashed_password = hashlib.md5(dataBase_password.encode())

        storage_client = storage.Client()

        bucket = client.bucket('userspasswords')
        blobs = storage_client.list_blobs('userspasswords')
            
        users = set()
        for blob in blobs:
            users.add(blob.name)
        print(users)

        #with bucket.open("r") as f:
        if username not in users:
            return 'Invalid User'            
            #print("Invalid User")
        else:
            blob = bucket.blob(username)
            with blob.open("r") as f:
                psw = f.read()
                
            if hashed_password.hexdigest() != psw:
                return 'Invalid Password'
                    #print(psw, hashed_password.hexdigest())
                    #print('Invalid Password')
            else:
                return username
                #print('name')
        

    def get_image(self, image_name):
        blobs = self.storage_client.list_blobs(self.bucket_name)
        for blob in blobs:
            if blob.name == image_name:
                with blob.open("rb") as b:
                    img_string = base64.b64encode(b.read())
                    img = 'data:image/png;base64,' + urllib.parse.quote(img_string)
                    return img

b = Backend("contentwiki")
