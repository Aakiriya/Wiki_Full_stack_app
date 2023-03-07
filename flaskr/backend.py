# TODO(Project 1): Implement Backend according to the requirements.
from flask import Blueprint,request, Flask, render_template, session
from google.cloud import storage
import hashlib
from io import BytesIO
import urllib, base64

client = storage.Client()
app = Flask(__name__)

class Backend:

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)

    def get_wiki_page(self, name):
        blob = self.bucket.blob(name) #search for th page with the given name
        if blob.exists(): 
            return blob.download_as_string() #if the page exists return the string
        else:
            return None #else return None

    def get_all_page_names(self):
        blobs = self.storage_client.list_blobs(self.bucket_name) #list all pages
        pages = {} #empty dict
        for blob in blobs: #read each blob
            if blob.content_type != 'image': #if is not an image
                pages[blob.name] = blob #save it in a dictionary
        return pages #return all the pages

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
        

    def get_image(self, image_name, blob_param=None):
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

if __name__ == 'main':
    unittest.main()