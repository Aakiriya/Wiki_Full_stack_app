from flask import Flask, request, render_template, session, redirect, url_for
from .backend import Backend, NoGenresFoundException


def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        """
        Returns:
            Redirects the user to the home page.
        """
        games = Backend("contentwiki").get_image(
            "games")  # get background image
        return render_template(
            "main.html", games=games)  # render main page with background image

    @app.route("/about")
    def about():
        """ 
        Gets background image along with about images for the three authors, then returns it to about page on render
        Args:
            None
        Returns:
            Redirects to About page with images of authors retrieved from cloud
        """
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
        """ Retrieve the file and wikipage name the user supplied in the form. Ensures the file was successfully retrieved and of valid
        type, then uses the wikipage name (representing the game's title) to search for valid genres associated with the game. For each
        valid genre, adds the genre along with the wikipage name to the Genres bucket, then adds the game to the contentwiki Bucket
        Args: None
        Returns:
            - "File was not uploaded correctly. Please try again." if no file is found in request/request made incorrectly
            - "Please upload a file." if no file found in request + wiki page name was supplied
            - "Uploaded successfully." if file and wiki page name was uploaded to the cloud successfully.

        """
        games = Backend("contentwiki").get_image("games")
        allowed_ext = {'txt', 'png', 'jpg', 'jpeg'}
        message = [
            "File was not uploaded correctly. Please try again.",
            "Please upload a file.", "File type not supported.",
            "Uploaded successfully."
        ]

        if request.method == 'POST':
            if 'file' not in request.files:
                return render_template("upload.html",
                                       message=message[0],
                                       games=games)
            file = request.files['file']

            if file.filename == "":
                return render_template("upload.html",
                                       message=message[1],
                                       games=games)
            elif file.filename.split('.')[1] not in allowed_ext:
                return render_template("upload.html",
                                       message=message[2],
                                       games=games)

            elif file:
                game_title = request.form.get("filename")
                b = Backend("contentwiki")
                g = Backend("game-genres")
                try:
                    genres = b.get_genre(game_title)
                    for genre in genres:
                        g.upload_genre(genre, game_title)
                except NoGenresFoundException:
                    # TODO(rakshith): Display popup when we fail to find genres for a game.
                    pass
                g.upload_genre("*All*", game_title)
                b.upload(game_title, file)
                return render_template("upload.html",
                                       message=message[3],
                                       games=games)
        return render_template("upload.html", games=games)

    @app.route('/login', methods=['POST', 'GET'])
    def sign_in():
        """ Retrieves the username and password the user supplied in the form and passes this info to the sign_in function in Backend
        to validate the username-password combination. If the username and password is correct, sets current session as the username
        currently signed in and redirects the user to the home page.
        Args: None
        Returns:
            - Redirects to home page if username-password combination is correct
            - Redirect to login page with "Invalid User" or "Invalid Password" message if the username or password is incorrect, respectively
        """
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
        """ Retrieve the username and password the user supplied via the form, then calls sign_up in Backend to write this information to 
        the cloud. After doing so, sets current session as the username currently signed in and redirects the user to the home page.
        Args: None
        Returns:
            Redirects the user to the home page as a logged in user.
        """
        games = Backend("contentwiki").get_image("games")
        if request.method == "POST":
            username = request.form['name']
            password = request.form['psw']
            b = Backend('userspasswords')
            b.sign_up(username, password)
            session['username'] = username
            return redirect('/')
        return render_template('signup.html', games=games)

    @app.route('/pages', methods=['GET', 'POST'])
    def pages():
        """ Get a list of all the genres to display via dropdown on the page upon render. If the user selects a genre, retrieve selected
        genre and find the games that match the genre from the Genre bucket, then return them hyperlinked (when clicked -> page)  
        Args: None
        Returns:
            - GET: Redirect to Pages page with a dropdown of all possible genres and a list of all game titles
            - POST: Redirect to Pages page with a dropdown of all possible genres and a list of all game titles matching the selected
            genre
        """
        #
        backend = Backend("game-genres")
        genres = backend.get_all_page_names()
        if request.method == 'GET':
            genre = "*All*"
        if request.method == 'POST':
            genre = request.form.get('genre')
        pages = backend.bucket.blob(genre).download_as_string().decode('utf-8')
        games = Backend("contentwiki").get_image("games")
        return render_template('pages.html',
                               section=genre,
                               pages=pages,
                               genres=genres,
                               games=games)

    @app.route('/pages/<name>')
    def show_page(name):
        """ Call the backend with the page's name to retrieve its contents, then decoded it via UTF-8 and render the page.   
        Args:
            name: String representing the name of the desired page
        Returns:
            Redirect to page with decoded page content
        """
        backend = Backend("contentwiki")
        content = backend.get_wiki_page(name)
        games = Backend("contentwiki").get_image("games")
        if content is not None:
            decoded_content = content.decode('utf-8')
            return render_template('pages.html',
                                   page_title=name,
                                   page_content=decoded_content,
                                   games=games)
        else:
            return f'Page {name} not found'

    @app.route("/logout")
    def logout():
        """ Sets current session to None (versus username of current user) and takes user to the home page
        Returns: Redirect to Home page
        """
        session['username'] = None
        return redirect('/')
