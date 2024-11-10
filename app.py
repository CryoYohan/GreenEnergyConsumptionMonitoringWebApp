from flask import Flask, render_template, redirect, url_for, request, flash, session
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = '@#@#@#@'
fullname:str = ''
email:str = ''
password:str = ''

# Configurations
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # For local testing only
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
PROJECT_ID = os.getenv("PROJECT_ID")
REDIRECT_URI = "http://localhost:9000/oauth2callback"

# Define the OAuth 2.0 flow
flow = Flow.from_client_config(
    client_config={
        "web": {
            "client_id": CLIENT_ID,
            "project_id": PROJECT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": CLIENT_SECRET,
            "redirect_uris": [REDIRECT_URI]
        }
    },
    scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_uri=REDIRECT_URI
)

# Google Login Route
@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url(prompt='consent')
    session["state"] = state
    return redirect(authorization_url)

# OAuth 2.0 Callback
@app.route("/oauth2callback")
def oauth2callback():
    try:
        flow.fetch_token(authorization_response=request.url)

        credentials = flow.credentials
        request_session = google.auth.transport.requests.Request()
        id_info = id_token.verify_oauth2_token(
            credentials.id_token, request_session, CLIENT_ID
        )

        # Retrieve user information
        session['email'] = id_info.get("email")
        session['name'] = id_info.get("name")

        flash(f"Welcome, {session['name']}!", 'success')
        return redirect(url_for("UserDashboardTemplate"))
    
    except ValueError as e:
        flash("Token verification failed. Please try again.", 'error')
        return redirect(url_for("Landing"))

# Dashboard Template Route
@app.route('/UserDashboardTemplate')
def UserDashboardTemplate():
    if 'name' in session:
        return render_template('UserDashboardTemplate.html', name=session['name'])
    flash("Please log in first.", 'warning')
    return redirect(url_for('Landing'))

# Manual Login Route
@app.route('/userlogin', methods=['POST'])
def userlogin():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == 'admin' and password == 'user':
        flash('Login Success!', 'success')
        return redirect(url_for('UserDashboardTemplate'))
    else:
        flash('Invalid Credentials!', 'error')
        return redirect(url_for('Landing'))

# User Registration Route
@app.route('/userregister', methods=['POST'])
def userregister():
    global fullname, email, password
    fullname = request.form['fullname']
    email = request.form['email']
    password = request.form['password']
    flash('Registration successful. Please log in.', 'success')
    return redirect(url_for('UserDashboardTemplate'))


# Landing Page
@app.route('/')
def landing():
    return render_template('Landing.html')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9000)
