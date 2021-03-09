import json

from flask import Flask, request, render_template
from models.user import UserModel
from models.log import LogModel
from db import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # we don't want Flask's modification tracker
app.secret_key = "sudeep"  # needs to be complicated


@app.before_first_request
def create_table():
    db.create_all()


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/form_login", methods=['GET', 'POST'])
def login():
    raw_data = request.cookies.get('locationData')
    try:
        location = json.loads(raw_data)
    except:
        return render_template("error_page.html")

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR']

    latitude = location['latitude']
    longitude = location['longitude']
    time = location['time']

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = UserModel.find_by_username(username)
        if user:
            if password == user.password:
                print(f"IP Address: {ip}")
                print(f"Latitude : {latitude}")
                print(f"Longitude : {longitude}")
                print(f"Time : {time}")

                log = LogModel(username, ip, latitude, longitude, time, None)
                log.save_to_db()

                return render_template("success.html", name=username)
            else:
                return render_template("login.html", info="** Wrong Password...")
        else:
            return render_template("login.html", info="** You are not a registered user. Please Sign Up to continue...")


@app.route("/register", methods=['GET', 'POST'])
def register():
    raw_data = request.cookies.get('locationData')
    try:
        location = json.loads(raw_data)
    except:
        return render_template("register.html", info="Location access denied. Please enable location to continue...")

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR']

    latitude = location['latitude']
    longitude = location['longitude']
    time = location['time']

    if request.method == "GET":
        return render_template("register.html")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phno = request.form['phno']

        if UserModel.find_by_username(username):
            return render_template("register.html", info="Username already taken. Please try a new username...")

        new_user = UserModel(username, password, phno, None, None, None, None, None)
        new_user.save_to_db()

        log = LogModel(username, ip, latitude, longitude, time, None)
        log.save_to_db()

        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Mobile Number: {phno}")     # apply all checks in html file
        print(f"IP Address: {ip}")
        print(f"Latitude : {latitude}")
        print(f"Longitude : {longitude}")
        print(f"Time : {time}")

        """
        Add all OTP checks here
        """

        return render_template("success.html", name=username)


@app.route('/user-logs')
def user_logs():
    return {'users': [user.json() for user in UserModel.query.all()]}


if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)
