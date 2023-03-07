from flask import Flask, request, render_template, session, redirect, url_for
from .backend import Backend

def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        games = Backend("contentwiki").get_image("games")
        return render_template("main.html", games=games)

    # TODO(Project 1): Implement additional routes according to the project requirements.
    
    @app.route("/about")    
    def about():
        b = Backend("contentwiki")
        b_pic = b.get_image('bethany')
        g_pic = b.get_image("gabriel")
        r_pic = b.get_image('rakshith')
        return render_template("about.html", b_pic = b_pic, g_pic = g_pic, r_pic = r_pic)
    
    @app.route("/upload", methods=['GET', 'POST'])
    def upload_file():
        allowed_ext = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}
        message = ["File was not uploaded correctly. Please try again.", "Please upload a file.", "File type not supported.", "Uploaded successfully."]
        if request.method == 'POST':
            if 'file' not in request.files:
                return render_template("upload.html", message=message[0])
            file = request.files['file']
            if file.filename == "":
                return render_template("upload.html", message=message[1])
            elif file.filename.split('.')[1] not in allowed_ext:
                return render_template("upload.html", message=message[2])
            elif file:
                b = Backend("contentwiki")
                b.upload(request.form.get("filename"), file)
                return render_template("upload.html", message=message[3])
        return render_template("upload.html")
        
    @app.route('/login', methods=['POST','GET'])
    def sign_in():
        if request.method == "POST":
            username = request.form['name']
            password = request.form['psw']
            b = Backend('userspasswords')
            info = b.sign_in(username, password)

            if info == 'Invalid User' or info == 'Invalid Password':
                return render_template('login.html', info=info)

            else:
                session['username'] = username
                return redirect('/')
        return render_template('login.html')

    @app.route('/signup', methods=['POST','GET'])
    def sign_up():
        if request.method == "POST":
            username = request.form['name']
            password = request.form['psw']
            b = Backend('userspasswords')
            b.sign_up(username, password)
            session['username'] = username
            return redirect('/')
        return render_template('signup.html')        
        
    @app.route('/pages')
    def pages():
        backend = Backend("contentwiki")
        pages = backend.get_all_page_names()
        return render_template("pages.html", pages = pages)
    
    @app.route('/pages/<name>')
    def show_page(name):
        backend = Backend("contentwiki")
        content = backend.get_wiki_page(name)
        #page_img = backend.get_image(name)
        if content is not None:
            return render_template("page.html", content=content.decode('utf-8'))
        else:
            return f'Page {name} not found'

    @app.route("/logout")    
    def logout():
        session['username'] = None
        return redirect('/')
