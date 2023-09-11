import sqlite3
from flask import render_template , request , redirect , session , Flask
from flask_session import Session
from helpers import login_required , strong_password , plan , bmr , apology



app = Flask(__name__)


#connecting to database
path = "C:\Azero\CS50\Final Project\members.db"


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/" , methods = ["GET" , "POST"])
@login_required
def index():
    conn = sqlite3.connect(path)
    db = conn.cursor()
    name = list(db.execute("SELECT * FROM users WHERE id = ? " , (session["user_id"] , )))[0][1]
    if request.method == "POST":
        weight = request.form.get("weight")
        height = request.form.get("height")
        age = request.form.get("age")
        gender = request.form.get("gender")
        activity = request.form.get("activity")
        cal = bmr(gender, weight , height , age , activity)
        meals = request.form.get("meals")
        my_plan = plan(cal , meals)
        if not my_plan :
            return apology("internet Connection is Weak Please Try Again!")
        #if there was an error and the meal plan is empty
        if not my_plan[list(my_plan.keys())[0]][1] :
            return apology("internet Connection is Weak Please Try Again!")
        return render_template("index.html" , name = name , plan = my_plan, cal = int(cal))
    return render_template("index.html" , name = name , plan = {}, cal = 0)






@app.route("/login" , methods = ["GET" , "POST"])
def login():
    #must have password and username
    #if not return the page with error
    #else: get username and password
    #check strong of the password
    #check if they exist
    #return to main
    session.clear()
    if request.method == "POST":
        if not request.form.get("password"):
            return render_template("login.html" , error = "Must provide Password")
        if not request.form.get("username"):
            return render_template("login.html" , error = "Must provide username")
        username = request.form.get("username")
        password = request.form.get("password")
        conn = sqlite3.connect(path)
        db = conn.cursor()
        rows = list(db.execute("SELECT * FROM users WHERE username = ?" ,(username , )))
        
        if len(rows) != 1:
            #there is no member
            return render_template("login.html" , error = "Haven't found username")
        if rows[0][2] != password:
            return render_template("login.html" , error = "Wrong Password!")
        session["user_id"] = rows[0][0]
        conn.close()
        return redirect("/")
    #if get
    return render_template("login.html", error = "")



#logout
@app.route("/logout" , methods = ["GET" , "POST"])
@login_required
def logout():
    session.clear()
    return redirect("/")


@app.route("/register" , methods = ["GET" , "POST"])
def register():
    #must have username and password
    #check if username is there or not
    #password is strong
    #insert to the database
    session.clear()
    if request.method == "GET" :
        return render_template("register.html" , error = "")
    #if post(clicking register)
    username = request.form.get("username")
    password = request.form.get("password")
    if not username:
        return render_template("register.html" , error = "MUST HAVE USERNAME!")
    conn = sqlite3.connect(path)
    db = conn.cursor()
    check_username = list(db.execute("SELECT * FROM users WHERE username = ?;" , (username,)))
    if check_username:
        return render_template("register.html" , error = "USERNAME IS ALREADY TAKEN")
    if not password :
        return render_template("register.html" , error = "MUST HAVE PASSWORD!")
    if not strong_password(password):
        return render_template("register.html" , error = "Your Password must be 8 letters long at least - should have a small letter, '@,!,#,$,%,&', big letter , and a number")
    db.executemany("INSERT INTO users (username , password) VALUES(? , ?);" , [(username , password)])
    conn.commit()
    user_id =list(db.execute("SELECT * FROM users WHERE username  = ? ;" , (username,)))[0][0]
    conn.close()
    session["user_id"] = user_id
    return redirect("/")
