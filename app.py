import os
import json, sqlite3
import requests

from flask import Flask, render_template, request, redirect, url_for, session
from twilio.rest import Client

from user import User
from twilio_credentials import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID


app = Flask(__name__)
app.secret_key = "secret"
generateotp_url = "https://api.generateotp.com/"


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == "GET":
        return render_template("login.html")  # showing the login page

    # fetching location of user
    location_data = get_user_location_data()
    latitude = location_data['latitude']
    longitude = location_data['longitude']
    time = location_data['time']

    # fetching ip of user
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR']

    username = request.form['username']
    password = request.form['password']

    user = User.find_by_username(username)

    if user:  # user exists
        if password == user.password:
            # password correct
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()

            query = "INSERT INTO logs VALUES(?,?,?,?,?, NULL)"
            cursor.execute(query, (user.username, ip, latitude, longitude, time))

            connection.commit()
            connection.close()

            return redirect(url_for('success'))
        else:  # wrong password
            return render_template('login.html', info="ERROR: Wrong Password. Please try again")
    else:  # user not registered
        return render_template('login.html', info="You are not a registered user. Please sign up to continue.")


@app.route("/register", methods=['GET', 'POST'])
def show_register_page():
    if request.method == "GET":
        return render_template("register.html")

    # ----- fetching location user -----
    location_data = get_user_location_data()
    latitude = location_data['latitude']
    longitude = location_data['longitude']
    time = location_data['time']

    # ----- fetching ip of user -----
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR']

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phone_number = request.form['phno']

        # storing in session; to be stored in db only if otp valid
        session['phone_number'] = phone_number
        session['username'] = username
        session['password'] = password
        session['longitude'] = longitude
        session['latitude'] = latitude
        session['time'] = time
        session['ip'] = ip

        if User.find_by_username(username):
            return render_template('register.html', info="Username already taken!")

        # -------- OTP VERIFICATION ---------
        otp_code = request_otp(phone_number)  # requesting for generation of otp from third party api
        msg = send_otp(phone_number, otp_code)  # sending otp to given number via message
        if msg:  # invalid phone number
            # error = msg
            return render_template('register.html', info="Invalid Phone Number. Please enter valid phone number.")
        # valid number
        return redirect(url_for('validate'))


@app.route("/validate", methods=['GET', 'POST'])
def validate():
    if request.method == "GET":
        return render_template('validate.html')

    input_otp = request.form['otp_code']
    phone_number = session['phone_number']
    isValid = validate_otp(input_otp, phone_number)

    if isValid:
        save_to_db()
        return redirect(url_for('success'))
    info = "Invalid OTP. Please try again."
    return render_template('validate.html', info=info)  # redirects to the same url u r in


@app.route("/success")
def success():  # opens the home page on success of entry
    return render_template('success.html')


def get_user_location_data():
    raw_data = request.cookies.get("locationData")
    try:
        location_data = json.loads(raw_data)
    except:
        return render_template("login.html", info="Location access denied. Please enable location to continue...")

    return location_data


def request_otp(phone_number):
    print("inside request_otp")
    req = requests.post(f"{generateotp_url}/generate", data={"initiator_id": phone_number})

    if req.status_code == 201:
        # OK
        data = req.json()  # converting to json
        return data['code']


def send_otp(phone_number, otp_code):
    print("inside send_otp")
    account_sid = TWILIO_ACCOUNT_SID  # from own twilio_credentials.py
    auth_token = TWILIO_AUTH_TOKEN  # from own twilio_credentials.py
    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            to=f"+91{phone_number}",
            from_="+17403278815",
            body=f"Your OTP is {otp_code}")

        print(message.sid)
        return None
    except:
        print("invalid phone number")
        return "Invalid phone number"


def validate_otp(otp_code, phone_number):
    req = requests.post(f"{generateotp_url}/validate/{otp_code}/{phone_number}")
    print(f"code: {req.status_code}")
    # data = req.json()
    # print(data['message'])

    if req.status_code == 200:
        print("ok")
        # OK
        data = req.json()
        print(data)
        return data['status']


def save_to_db():
    phone_number = session['phone_number']
    username = session['username']
    password = session['password']
    longitude = session['longitude']
    latitude = session['latitude']
    time = session['time']
    ip = session['ip']

    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()

    query = "INSERT INTO users VALUES (NULL, ?, ?, ?, NULL, NULL, NULL, NULL, NULL)"
    cursor.execute(query, (username, password, phone_number))

    query = "INSERT INTO logs VALUES (?,?,?,?, ?, NULL)"
    cursor.execute(query, (username, ip, latitude, longitude, time))

    connection.commit()
    connection.close()

    return redirect(url_for('success'))


app.run(port=5000, debug=True)