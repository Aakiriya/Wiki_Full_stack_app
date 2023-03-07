from flaskr import create_app
from flask import session
import pytest
from unittest import mock
from unittest.mock import Mock, MagicMock, patch
from .backend import Backend
import io 

# See https://flask.palletsprojects.com/en/2.2.x/testing/ 
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_home(client):
    with client.session_transaction() as session:
        session['username'] = None
    resp = client.get("/")
    assert resp.status_code == 200
    response = resp.data.decode('utf-8')
    login = '<a href="/login">Login</a>\n'
    assert login in response
    with client.session_transaction() as session:
        session['username'] = 'me'
    resp = client.get("/").data.decode('utf-8')
    user =  '<a> | me |</a>'
    logout = '<a href="/logout">Logout</a>'
    assert user in resp 
    assert logout in resp

def test_about(client):
    resp = client.get("/about").data.decode('utf-8')
    about = '<p> This wiki serves as a hub to all things video games! </p>'
    assert about in resp

def test_upload(client):
    resp = client.post("/upload").data.decode('utf-8')
    assert "File was not uploaded correctly." in resp

    data = {
        'file': (io.BytesIO(b"text data"), ''),
        'filename': 'test'
    }
    resp = client.post("/upload", data=data,content_type='multipart/form-data')
    assert "Please upload a file." in resp.data.decode('utf-8')

    data['file'] = (io.BytesIO(b"text data"), 'test.idk')
    resp = client.post("/upload", data=data,content_type='multipart/form-data')
    assert "File type not supported." in resp.data.decode('utf-8')

    data['file'] = (io.BytesIO(b"text data"), 'test.txt')
    with mock.patch('flaskr.backend.storage.Client'):
        resp = client.post("/upload", data=data,content_type='multipart/form-data')
        assert "Uploaded successfully." in resp.data.decode('utf-8')

def test_logout(client):
    with client.session_transaction() as sess:
        sess['username'] = "beth"
    resp = client.get("/logout")
    assert "redirect" in resp.data.decode('utf-8')
    with client.session_transaction() as sess:
        assert sess['username'] is None

def test_pages_page(client): #Test if the pages html actually displays the actual pages
    resp = client.get("/pages")
    assert resp.status_code == 200
    assert b"<h3>Pages Contained in this Wiki</h3>" in resp.data
    assert b"<a href=\"/pages/" in resp.data

def test_signup_route(client): #Tests if the signup page is routing properly and it displays the intended message 
    resp = client.get("/signup").data.decode('utf-8')
    assert '<p>Please fill in this form to create an account.</p>' in resp

def test_signin_route(client): #Tests if the signup page is routing properly and it displays the intended message 
    resp = client.get("/login").data.decode('utf-8')
    assert '<p>Please fill in this form to sign in to your account.</p>' in resp
