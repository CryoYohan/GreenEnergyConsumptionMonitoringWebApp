from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import os
from dotenv import load_dotenv
from appliances import appliances as appliancesdict

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
    return redirect(url_for('landing')) if not session.get("name") else render_template('UserDashboardTemplate.html')

@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = 'no-cache,no-store,must-revalidate'
    #response.headers['Pragma'] = 'no-cache'
    return response 

@app.route("/logout")
def logout():
    session['name'] = None
    return redirect(url_for("landing"))

# Manual Login Route
@app.route('/userlogin', methods=['POST'])
def userlogin():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == 'admin' and password == 'user':
        session['name'] = username
        flash("LOGIN SUCCESSFUL!", "info")
        return redirect(url_for('UserDashboardTemplate'))
    else:
        flash('Invalid Credentials!', 'error')
        return redirect(url_for('landing'))


@app.route('/userregister', methods=['POST'])
def userregister():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    password = request.form.get('password')
    return redirect(url_for('setup'))


# User Registration Route
@app.route('/userregister1', methods=['POST'])
def userregister1():
    global fullname, email, password
    fullname = request.form['fullname']
    email = request.form['email']
    password = request.form['password']
    flash('Registration successful. Please log in.', 'success')
    return redirect(url_for('UserDashboardTemplate'))

@app.route('/setupTariff')
def setupTariff():
    return render_template('setupTariff.html')


@app.route('/panelsetup')
def panelsetup():
    return render_template('panelsetup.html')

@app.route('/setupPanels', methods=['POST'])
def setupPanels():
    if request.method == 'POST':
        print(request.form.get('solarpanels'))
        print(request.form['quantity'])
    return redirect(url_for('setupTariff'))

@app.route('/setupAppliances', methods=['POST'])
def setupAppliances():
    if request.method == 'POST':
        print(request.form.getlist('mycheckbox'))
        return redirect(url_for('panelsetup'))
    return redirect(url_for('panelsetup'))

@app.route('/setup')
def setup():
    return render_template('setup.html', appliances=appliancesdict)
# Landing Page
@app.route('/')
def landing():
    return render_template('Landing.html')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9000)
