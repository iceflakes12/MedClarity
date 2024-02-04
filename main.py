from flask import Flask, url_for, redirect, request, render_template, jsonify, session
import sqlite3
import pytesseract
import numpy as np
import base64
import cv2

app = Flask(__name__)
app.secret_key = "23d/fida6*dwk%$dz"

@app.route("/", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        Json = request.get_json()
        if valid_login(Json['username'], Json['password']):
            session['username'] = Json['username']
            return jsonify({"result": "success"})
        return jsonify({"result": "Incorrect password or username"})
    return render_template("login.html")

@app.route("/create account", methods = ["POST", "GET"])
def create_account():
    if request.method == "POST":
        Json = request.get_json()
        if unique_username(Json['username']):
            if Json['password'] == Json['confirm_password']:
                create_account_backend(Json['username'], Json['password'])
                return jsonify({"result": "Successful account creation"})
            return jsonify({"result": "Password and confirm password do not match!"})
        return jsonify({"result": "Username not unique!"})
    return render_template("createaccount.html")

@app.route("/successful login")
def proceed():
    if 'username' in session:
        return render_template("success.html")
    return redirect(url_for("login"))

@app.route("/homepage")
def homepage():
    if 'username' in session:
        return render_template("homepage.html")
    return redirect(url_for("login"))

@app.route("/report")
def report():
    if 'username' in session:
        return render_template("report.html")
    return redirect(url_for("login"))

@app.route("/process report", methods = ["POST"])
def process_report():
    if 'username' in session:
        if request.method == "POST":
            image_data = request.get_json()
            output_data = gen_ai_report(image_data)
            if output_data.strip() == '':
                return jsonify({"result": 'Image is unclear or does not contain text, try again!'})
            output_data = gen_ai_chatbot(output_data)
            return jsonify({"result": output_data})


@app.route("/diagnosis")
def diagnosis():
    if 'username' in session:
        conn = sqlite3.connect('storage.db')
        c = conn.cursor()
        disease_row = tuple(c.execute('SELECT disease_name FROM diagnosis'))
        c.close()
        return render_template("diagnosis.html", diseases= disease_row)
    return redirect(url_for("login"))

@app.route("/diagnosis/<disease_name>")
def render_diagnosis(disease_name):
    if 'username' in session:
        conn = sqlite3.connect('storage.db')
        c = conn.cursor()
        query_row = tuple(c.execute('SELECT path FROM diagnosis WHERE disease_name =?', (disease_name,)))[0]
        c.close()
        return render_template(query_row[0])
    return redirect(url_for("login"))

@app.route("/chatterbot", methods = ["POST", "GET"])
def chatterbot():
    if 'username' in session:
        if request.method == "POST":
            return jsonify({"result": gen_ai_chatbot(request.get_json())})
        return render_template("chatterbot.html")
    return redirect(url_for("login"))

@app.route("/change password", methods = ["POST", "GET"])
def change_password():
    if 'username' in session:
        if request.method == "POST":
            Json = request.get_json()
            if valid_login(session['username'], Json['old_password']):
                if Json['password'] == Json['confirm_password']:
                    change_password_backend(session['username'], Json['password'])
                    return jsonify({"result": "Successful password change"})
                return jsonify({"result": "Password and confirm password do not match!"})
            return jsonify({"result": "Incorrect old password!"})
        return render_template("cp.html")
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for("login"))

def change_password_backend(username, new_password):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    insertTuple = (new_password, username)
    c.execute('UPDATE login SET password =? WHERE username =?', insertTuple)
    conn.commit()
    c.close()

def unique_username(username):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    usernameTuple = (username,)
    return_entry = tuple(c.execute('SELECT password FROM login WHERE username=?', usernameTuple))
    c.close()
    if len(return_entry) > 0:
        return False
    return True

def create_account_backend(username, password):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    insertTuple = (username, password)
    c.execute('INSERT INTO login (username, password) VALUES (?,?)', insertTuple)
    conn.commit()
    c.close()

def valid_login(username, password):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    usernameTuple = (username,)
    return_entry = tuple(c.execute('SELECT password FROM login WHERE username=?', usernameTuple))
    c.close()
    if len(return_entry) > 0:
        return_value = return_entry[0][0]
    else:
        return False
    return (return_value == password)

def gen_ai_report(image):
    binary_data = base64.b64decode(image)

    np_array = np.frombuffer(binary_data, np.uint8)
    cv2_workable_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    gray_image = cv2.cvtColor(cv2_workable_image, cv2.COLOR_BGR2GRAY)

    text_from_new_image = pytesseract.image_to_string(gray_image)

    return text_from_new_image


from medical import analyze_symptoms

def gen_ai_chatbot(user_input):
    response = analyze_symptoms(user_input)
    return response