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


def test_home_logged_out(client):
    """ Sets the session so that no user is logged in, then retrieves the home page and asserts that the user has option to login
    (meaning that they are currently logged out) within the page contents
    """
    with client.session_transaction() as session:
        session['username'] = None

    with mock.patch('flaskr.backend.storage.Client'):
        resp = client.get("/")
        response = resp.data.decode('utf-8')
        login = '<a href="/login">Login</a>\n'
        assert login in response


def test_home_logged_in(client):
    """ Sets the user as logged in, retrieves the home page, and asserts that the user has option to logout (meaning they are currently
    logged in) within the page contents
    """
    with client.session_transaction() as session:
        session['username'] = 'me'

    with mock.patch('flaskr.backend.storage.Client'):
        resp = client.get("/").data.decode('utf-8')
        logout = '<a href="/logout">Logout</a>'
        assert  logout in resp


def test_about(client):
    """ Retrieves the about page and asserts that the correct wiki description appears on the page contents """
    with mock.patch('flaskr.backend.storage.Client'):
        resp = client.get("/about").data.decode('utf-8')
        about = '<h3> This wiki serves as a hub to all things video games! </h3>'
        assert about in resp


def test_upload_error_file(client):
    """ Gets upload route and asserts correct error message is displayed for a file error """
    with mock.patch('flaskr.backend.storage.Client'):
        resp = client.post("/upload").data.decode('utf-8')
        assert "File was not uploaded correctly." in resp


def test_upload_no_file(client):
    """ Gets upload route and asserts correct error message is displayed for no file found """
    data = {'file': (io.BytesIO(b"text data"), ''), 'filename': 'test'}
    with mock.patch('flaskr.backend.storage.Client'):
        resp = client.post("/upload",
                           data=data,
                           content_type='multipart/form-data')
        assert "Please upload a file." in resp.data.decode('utf-8')


def test_upload_wrong_file(client):
    """ Gets upload route and asserts correct error message is displayed for unsupported file extension """
    data = {'file': (io.BytesIO(b"text data"), 'test.idk'), 'filename': 'test'}
    with mock.patch('flaskr.backend.storage.Client'):
        resp = client.post("/upload",
                           data=data,
                           content_type='multipart/form-data')
        assert "File type not supported." in resp.data.decode('utf-8')


def test_upload_success(client):
    """ Gets upload route and asserts success message is displayed for a successful file upload """
    data = {'file': (io.BytesIO(b"text data"), 'test.txt'), 'filename': 'test'}
    with mock.patch('flaskr.backend.storage.Client'):
        resp = client.post("/upload",
                           data=data,
                           content_type='multipart/form-data')
        assert "Uploaded successfully." in resp.data.decode('utf-8')


def test_logout(client):
    """ Sets up user as logged in, calles the /logout route and asserts the session's user is None (meaning the user is logged out) """
    with client.session_transaction() as sess:
        sess['username'] = "beth"

    resp = client.get("/logout")
    assert "redirect" in resp.data.decode('utf-8')

    with client.session_transaction() as sess:
        assert sess['username'] is None


def test_pages(client):
    """ Test if the pages html actually displays the actual pages """
    with mock.patch('flaskr.backend.storage.Client'):
        resp = client.get("/pages")
        assert resp.status_code == 200
        assert b"Pages" in resp.data


def test_signup_route(client):
    """ Tests if the signup page is routing properly and it displays the intended message """
    with mock.patch('flaskr.backend.storage.Client'):
        resp = client.get("/signup").data.decode('utf-8')
        assert '<p>Please fill in this form to create an account. A valid Password Should have at least one number, Should have at least one uppercase and one lowercase character, Should have at least one special symbol and Should be between 6 to 20 characters long.</p>' in resp


def test_signin_route(client):
    """ Tests if the signup page is routing properly and it display the intended message """
    with mock.patch('flaskr.backend.storage.Client'):
        resp = client.get("/login").data.decode('utf-8')
        assert '<p>Please fill in this form to sign in to your account.</p>' in resp


""" Test if the code to check valid email works by givin a valid email and not getting Invalid email displayed """


def test_valid_email(client):
    # with mock.patch('flaskr.backend.storage.Client'):
    with client.session_transaction() as session:
        session['username'] = None

    data = {
        'name': None,
        'psw': 'Password123@',
        'email_add': 'testuser@test.com'
    }

    resp = client.post('/signup', data=data, follow_redirects=True)
    assert b"Invalid Email" not in resp.data


""" Test if the code to check valid email works by givin an invalid email and getting Invalid email displayed """


def test_invalid_email(client):
    with client.session_transaction() as session:
        session['username'] = None

    data = {
        'name': 'testuser',
        'psw': 'Password123@',
        'email_add': 'testusertest.com'
    }
    resp = client.post('/signup', data=data, follow_redirects=True)

    assert b"Invalid Email" in resp.data


""" Test if the code to check valid password works by givin a valid password and not getting Invalid password displayed """


def test_valid_password(client):
    with client.session_transaction() as session:
        session['username'] = None

    data = {
        'name': None,
        'psw': 'Password123@',
        'email_add': 'testuser@test.com'
    }
    resp = client.post('/signup', data=data, follow_redirects=True)
    assert b"Invalid Password" not in resp.data


""" Test if the code to check valid password works by givin a valid password and getting Invalid password displayed """


def test_invalid_password(client):
    with client.session_transaction() as session:
        session['username'] = None

    data = {
        'name': 'testuser',
        'psw': 'password',
        'email_add': 'testuser@test.com'
    }
    resp = client.post('/signup', data=data, follow_redirects=True)

    assert b"Invalid Password" in resp.data
