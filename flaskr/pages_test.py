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
    # set user as not logged in
    with client.session_transaction() as session:
        session['username'] = None

    # get home page, assert it was successful and that the user has option to login within the page contents
    resp = client.get("/")
    assert resp.status_code == 200
    response = resp.data.decode('utf-8')
    login = '<a href="/login">Login</a>'
    assert login in response

    # set user as logged in
    with client.session_transaction() as session:
        session['username'] = 'me'

    # get home page, assert it was successful and that the user has option to logout within the page contents
    resp = client.get("/").data.decode('utf-8')
    user = '<a>| me |</a>'
    logout = '<a href="/logout">Logout</a>'
    assert user in resp
    assert logout in resp


def test_about(client):
    # get about page and assert information about wiki is returned
    with mock.patch('flaskr.backend.storage.Client'):
        resp = client.get("/about").data.decode('utf-8')
        about = '<h3> This wiki serves as a hub to all things video games! </h3>'
        assert about in resp


def test_upload(client):
    # get upload route and assert "file is incorrect"
    resp = client.post("/upload").data.decode('utf-8')
    assert "File was not uploaded correctly." in resp

    data = {'file': (io.BytesIO(b"text data"), ''), 'filename': 'test'}
    # get upload route with no file supplied and assert to upload file
    resp = client.post("/upload", data=data, content_type='multipart/form-data')
    assert "Please upload a file." in resp.data.decode('utf-8')

    # get upload route and pass in incorrect file extension, assert that the file type is not supported
    data['file'] = (io.BytesIO(b"text data"), 'test.idk')
    resp = client.post("/upload", data=data, content_type='multipart/form-data')
    assert "File type not supported." in resp.data.decode('utf-8')

    # get upload route and pass in correct file type, assert upload was successful
    data['file'] = (io.BytesIO(b"text data"), 'test.txt')
    with mock.patch('flaskr.backend.storage.Client'):
        resp = client.post("/upload",
                           data=data,
                           content_type='multipart/form-data')
        assert "Uploaded successfully." in resp.data.decode('utf-8')


def test_logout(client):
    # set up user as logged in
    with client.session_transaction() as sess:
        sess['username'] = "beth"

    # get logout route
    resp = client.get("/logout")
    assert "redirect" in resp.data.decode('utf-8')

    # assert user is logged out
    with client.session_transaction() as sess:
        assert sess['username'] is None


def test_pages_page(
        client):  #Test if the pages html actually displays the actual pages
    resp = client.get("/pages")
    assert b"<h1>Pages Contained in this Wiki</h1>" in resp.data
    assert b"<a href=\"/pages/" in resp.data


def test_signup_route(
    client
):  #Tests if the signup page is routing properly and it displays the intended message
    resp = client.get("/signup").data.decode('utf-8')
    assert '<p>Please fill in this form to create an account.</p>' in resp


def test_signin_route(
    client
):  #Tests if the signup page is routing properly and it displays the intended message
    resp = client.get("/login").data.decode('utf-8')
    assert '<p>Please fill in this form to sign in to your account.</p>' in resp


def test_editor(client):
    # get editor page and assert that TinyMCE API script tag is present in the HTML
    with mock.patch('flaskr.backend.storage.Client'):
        resp = client.get("/tinyedit").data.decode('utf-8')
        assert '<script src="/static/tinymce/tinymce.min.js"></script>' in resp
