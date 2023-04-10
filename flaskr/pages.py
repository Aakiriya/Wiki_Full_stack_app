from flask import Flask, request, render_template, session, redirect, url_for
from .backend import Backend
import re

def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        games = Backend("contentwiki").get_image(
            "games")  # get background image
        return render_template(
            "main.html", games=games)  # render main page with background image

    # TODO(Project 1): Implement additional routes according to the project requirements.

    @app.route("/about")
    def about():
        # gets background image along with about images for the three authors, then returns it to about page on render
        games = Backend("contentwiki").get_image("games")
        b = Backend("contentwiki")
        b_pic = b.get_image('bethany')
        g_pic = b.get_image("gabriel")
        r_pic = b.get_image('rakshith')
        return render_template("about.html",
                               b_pic=b_pic,
                               g_pic=g_pic,
                               r_pic=r_pic,
                               games=games)

    @app.route("/upload", methods=['GET', 'POST'])
    def upload_file():
        # gets background image
        games = Backend("contentwiki").get_image("games")
        # sets allowed file types, messages to return based on situation
        allowed_ext = {'txt', 'png', 'jpg', 'jpeg'}
        message = [
            "File was not uploaded correctly. Please try again.",
            "Please upload a file.", "File type not supported.",
            "Uploaded successfully."
        ]

        if request.method == 'POST':
            # if no file is found in request/request made incorrectly, return first error message
            if 'file' not in request.files:
                return render_template("upload.html",
                                       message=message[0],
                                       games=games)
            file = request.files['file']

            # if no file found in request + wiki page name was supplied, return second error message
            if file.filename == "":
                return render_template("upload.html",
                                       message=message[1],
                                       games=games)
            elif file.filename.split('.')[1] not in allowed_ext:
                return render_template("upload.html",
                                       message=message[2],
                                       games=games)

            # if file is correct, pass file and filename to upload() function and return success message
            elif file:
                b = Backend("contentwiki")
                b.upload(request.form.get("filename"), file)
                return render_template("upload.html",
                                       message=message[3],
                                       games=games)
        return render_template("upload.html", games=games)

    @app.route('/login', methods=['POST', 'GET'])
    def sign_in():
        games = Backend("contentwiki").get_image("games")
        if request.method == "POST":
            username = request.form['name']
            password = request.form['psw']
            b = Backend(
                'userspasswords'
            )  #passes the unsername and password entered to the login function in Backend class
            info = b.sign_in(username, password)

            if info == 'Invalid User' or info == 'Invalid Password':  #if the passward or username is invalid it renders back to the login page and displays the error message
                return render_template('login.html', info=info, games=games)

            else:
                session[
                    'username'] = username  #adds the username to the session
                return redirect('/')
        return render_template('login.html', games=games)

    @app.route('/signup', methods=['POST', 'GET'])
    def sign_up():
        games = Backend("contentwiki").get_image("games")
        if request.method == "POST":
            username = request.form['name']
            password = request.form['psw']
            email = request.form['email_add']
            regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            regex_psw = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
            b = Backend('userspasswords')

            if not (re.fullmatch(regex_email, email)):
                info = "Invalid Email"
                return render_template('signup.html', info=info, games=games)      

            # compiling regex
            pat = re.compile(regex_psw)
     
            # searching regex                
            mat = re.search(pat, password)
     
            # validating conditions
            if not mat:
                info = "Invalid Password"
                return render_template('signup.html', info=info, games=games)      

 
            info = b.sign_up(
                username, password, email
            )  #passes the unsername and password entered to the signup function in Backend class

            if info == 'Username already exsists':
                return render_template('signup.html', info=info, games=games)
            else:
                session['username'] = username  #adds the username to the session
                return redirect('/')
        return render_template('signup.html', games=games)

    @app.route('/pages')
    def pages():
        backend = Backend(
            "contentwiki")  #Call the backend with the buckets name
        pages = backend.get_all_page_names(
        )  #call the get allpages and save the dictionary in pages
        games = Backend("contentwiki").get_image("games")  #background
        return render_template(
            'pages.html', pages=pages,
            games=games)  #render the pages reading the dictionary

    @app.route('/pages/<name>')
    def show_page(name):
        backend = Backend(
            "contentwiki")  #Call the backend with the buckets name
        content = backend.get_wiki_page(
            name)  #send the name of tha page we want ot show
        games = Backend("contentwiki").get_image("games")  #background
        if content is not None:
            decoded_content = content.decode(
                'utf-8')  #decode the text from the page
            return render_template('pages.html',
                                   page_title=name,
                                   page_content=decoded_content,
                                   games=games)  #send the text for rendering
        else:
            return f'Page {name} not found'

    @app.route("/logout")
    def logout():
        # when user logs out, set session username to None, then redirect to home page
        session['username'] = None
        return redirect('/')

    @app.route('/profile', methods=['POST', 'GET'])
    def profile():
        user_name = session['username']
        print(user_name)
        games = Backend("contentwiki").get_image("games")
        b = Backend('userspasswords')
        profile_details = b.profile(user_name)
        profile_pic = b.get_image(profile_details[-1])
        return render_template('profile.html', username = user_name, 
                                               email = profile_details[1],
                                               bio = profile_details[2],
                                               favorite_games = profile_details[3],
                                               favorite_genres = profile_details[4],
                                               favorite_developers = profile_details[-2],
                                               profile_pic_path = profile_pic,
                                               games = games)

