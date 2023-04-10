from flask import Flask, request, render_template, session, redirect, url_for, Response
from .backend import Backend
import re
def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        return render_template("main.html") # render main page with background image

    # TODO(Project 1): Implement additional routes according to the project requirements.
    
    @app.route("/about")    
    def about():
        # gets background image along with about images for the three authors, then returns it to about page on render
        b = Backend("contentwiki")
        b_pic = b.get_image('bethany')
        g_pic = b.get_image("gabriel")
        r_pic = b.get_image('rakshith')
        return render_template("about.html", b_pic = b_pic, g_pic = g_pic, r_pic = r_pic)
    
    @app.route("/upload", methods=['GET', 'POST'])
    def upload_file():
        # sets allowed file types, messages to return based on situation
        allowed_ext = {'html', 'txt', 'png', 'jpg', 'jpeg'}
        message = ["File was not uploaded correctly. Please try again.", "Please upload a file.", "File type not supported.", "Uploaded successfully."]
        
        if request.method == 'POST':
            # if no file is found in request/request made incorrectly, return first error message
            if 'file' not in request.files:
                return render_template("upload.html", message=message[0])
            file = request.files['file']

            # if no file found in request + wiki page name was supplied, return second error message
            if file.filename == "":
                return render_template("upload.html", message=message[1])

            #elif file.filename.split('.')[1] not in allowed_ext: old code
            elif file.filename[len(file.filename) - 3:] in allowed_ext and file: #check last 3 characters for extension 'txt', 'png', 'jpg', 'jpeg'
                b = Backend("contentwiki")
                b.upload(request.form.get("filename"), file)
                return render_template("upload.html", message=message[3])
            
            elif file.filename[len(file.filename) - 4:] in allowed_ext and file: #check last 4 characters for extension 'html'
                b = Backend("contentwiki")
                b.upload(request.form.get("filename"), file)
                return render_template("upload.html", message=message[3])

            #if the file extension is not in the allowed extension
            else:
                return render_template("upload.html", message=message[2])
        return render_template("upload.html")
        
    @app.route('/login', methods=['POST','GET'])
    def sign_in():
        if request.method == "POST":
            username = request.form['name']
            password = request.form['psw']
            b = Backend('userspasswords')#passes the unsername and password entered to the login function in Backend class
            info = b.sign_in(username, password)

            if info == 'Invalid User' or info == 'Invalid Password':#if the passward or username is invalid it renders back to the login page and displays the error message
                return render_template('login.html', info=info)

            else:
                session['username'] = username #adds the username to the session
                return redirect('/')
        return render_template('login.html')

    @app.route('/signup', methods=['POST', 'GET'])
    def sign_up():
        if request.method == "POST":
            username = request.form['name']
            password = request.form['psw']
            email = request.form['email_add']
            regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            regex_psw = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
            b = Backend('userspasswords')

            if not (re.fullmatch(regex_email, email)):
                info = "Invalid Email"
                return render_template('signup.html', info=info)      

            # compiling regex
            pat = re.compile(regex_psw)
     
            # searching regex                
            mat = re.search(pat, password)
     
            # validating conditions
            if not mat:
                info = "Invalid Password"
                return render_template('signup.html', info=info)      

 
            info = b.sign_up(
                username, password, email
            )  #passes the unsername and password entered to the signup function in Backend class

            if info == 'Username already exsists':
                return render_template('signup.html', info=info)
            else:
                session['username'] = username  #adds the username to the session
                return redirect('/')
        return render_template('signup.html')    
        
    @app.route('/pages')
    def pages():
        backend = Backend("contentwiki") #Call the backend with the buckets name
        pages = backend.get_all_page_names() #call the get allpages and save the dictionary in pages
        return render_template('pages.html', pages = pages) #render the pages reading the dictionary
    
    @app.route('/pages/<name>')
    def show_page(name):
        backend = Backend("contentwiki")
        content, mime_type = backend.get_wiki_page(name)
        page_title = f'{name}'
        if content is not None:
            return render_template('page.html', content=content.decode(), page_title=page_title)
        else:
            return f'Page {name} not found'


    @app.route("/logout")    
    def logout():
        # when user logs out, set session username to None, then redirect to home page
        session['username'] = None
        return redirect('/')

    @app.route("/tinyedit", methods=['POST','GET']) 
    def editor():
        return render_template('tinyedit.html')
