from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import os
from dotenv import load_dotenv
from appliances import appliances as appliancesdict
from dbhelper import Databasehelper

load_dotenv()

app = Flask(__name__)
app.secret_key = '@#@#@#@'
db = Databasehelper()
fullname:str = ''
email:str = ''
password:str = ''
user_table = 'user'




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

@app.route('/SimulationPage')
def SimulationPage():
    return render_template('SimulationPage.html')

@app.route('/CarbonEmission')
def CarbonEmission():
    return render_template('CarbonEmissionDash.html')

@app.route('/GreenEnergyDash')
def GreenEnergyDash():
    return render_template('GreenEnergyDash.html')

@app.route('/CostEstimationDash')
def CostEstimationDash():
    return render_template('CostEstimationDash.html')

@app.route('/AppliancesDash')
def AppliancesDash():
    return render_template('AppliancesDash.html')

@app.route('/UserDashboardContent')
def UserDashboardContent():
    return render_template('UserDashboardContent.html')

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

        email = id_info.get("email")
        fullname = id_info.get("name")
        # Retrieve user information
        session['email'] = email
        session['name'] = fullname
        print(email, fullname)
        user_record_exist = db.find_user(table=user_table,email= id_info.get("email"))
        if not user_record_exist:
            db.add_user(table=user_table,email=email,fullname=fullname)

        flash(f"Welcome, {session['name']}!", 'success')
        return redirect(url_for("UserDashboardTemplate"))
    
    except ValueError as e:
        flash("Token verification failed. Please try again.", 'error')
        return redirect(url_for("Landing"))

# Dashboard Template Route
@app.route('/UserDashboardTemplate')
def UserDashboardTemplate():
    global fullname
    if not session.get("name"):
        flash("Please log in first.", "error")
        return redirect(url_for('landing'))
    pie_data = {
        'labels': ['Apples', 'Oranges', 'Bananas', 'Grapes'],
        'values': [50, 20, 15, 15],
    }


    return render_template('UserDashboardTemplate.html',fullname=fullname,pie_data=pie_data)


@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = 'no-cache,no-store,must-revalidate'
    #response.headers['Pragma'] = 'no-cache'
    return response 

@app.route("/logout")
def logout():
    session['name'] = None
    session['email'] = None
    return redirect(url_for("landing"))
# Validate email 
def email_exists(email:str):
    record = db.find_user(table=user_table, email=email)
    return True if record else False


# Manual Login Route
@app.route('/userlogin', methods=['POST'])
def userlogin():
    global fullname
    email = request.form.get('email')
    password = request.form.get('password')
    records = db.getall_users(table=user_table)
    print(records)
    for record in records:
        if record['email'] == email and record['password'] == password:
            session['name'] = email
            fullname = record['fullname'].split(' ')[0] + ' ' + record['fullname'].split(' ')[-1]
            flash("LOGIN SUCCESSFUL!", "info")
            return redirect(url_for('UserDashboardTemplate'))
    else:
        flash('Invalid Credentials!', 'error')
        return redirect(url_for('landing'))


@app.route('/userregister', methods=['POST'])
def userregister():
    global fullname
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    password = request.form.get('password')
    if email_exists(email=email):
        flash('This email has already been registered!')
    else:
        db.add_user(table=user_table,email=email,fullname=fullname, password=password)

    session['name'] = email

    flash(f"Welcome {fullname}, please complete the setup.", "success")
    return redirect(url_for('setup'))



@app.route('/submit_tariff', methods=['POST'])
def submit_tariff():
    # Retrieve JSON data from request
    data = request.get_json()
    provider = data.get('provider')
    tariff_rate = data.get('tariff_rate')
    tariff_type = data.get('tariff_type')

    # Debug print statements
    print(f"Provider: {provider}")
    print(f"Tariff Rate: {tariff_rate} kWh")
    print(f"Tariff Type: {tariff_type}")

    # Check if session['email'] is set
    if not session.get('name'):
        flash("Session expired or invalid. Please log in again.", "error")
        return jsonify({"redirect": url_for('landing')})

    # Confirm user session before redirecting to the dashboard
    session['registered_user'] = email  
    flash("Setup completed successfully!", "success")
    return jsonify({"redirect": url_for('UserDashboardTemplate')})


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
        picked_appliances:list = request.form.getlist('mycheckbox')
        print(picked_appliances)
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
