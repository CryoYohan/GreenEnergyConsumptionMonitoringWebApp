from flask import Flask, request, redirect, url_for, session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os

app = Flask(__name__)
app.secret_key = "@#@#@#"

# Google OAuth 2.0 Configuration
CLIENT_ID = "662544393470-4uh51jghknm4e696nq4o0v1qak81oper.apps.googleusercontent.com"

@app.route("/")
def index():
    user_name = session.get("user_name", "Guest")
    return f"Hello, {user_name}! <a href='/login'>Login with Google</a>"

@app.route("/login2")
def login2():
    return redirect(url_for("login2"))
@app.route("/login")
def login():
    return redirect(url_for("index"))

@app.route("/oauth2callback")
def oauth2callback():
    token = request.args.get("credential")
    try:
        id_info = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)
        session["user_name"] = id_info.get("name")
        session["user_email"] = id_info.get("email")
        return redirect(url_for("index"))
    except ValueError:
        return "Token verification failed"

if __name__ == "__main__":
    app.run(debug=True)