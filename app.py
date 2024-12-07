from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import os
from dotenv import load_dotenv
from appliances import appliances as appliancesdict
from dbhelper import Databasehelper
from simulator import Simulator

load_dotenv()

app = Flask(__name__)
app.secret_key = '@#@#@#@'
db = Databasehelper()
simulate = Simulator()

fullname:str = ''
email:str = ''
password:str = ''
user_table:str = 'user'
appliances:list = []
days_in_week:list = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'] 
weeklydata:list = []
panel_type:str = ''
panel_quantity:int = 0
tariffcompany:str = ''
tariff_rate:int = 0
tariff_type:str = ''



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

@app.route('/Settings')
def Settings():
    pie_data = {
        'labels': ['Apples', 'Oranges', 'Bananas', 'Grapes'],
        'values': [50, 20, 15, 15],
        }
    return render_template('Settings.html',fullname=session.get('name'), pie_data=pie_data) if not session.get('name') == None else redirect(url_for('landing'))

@app.route('/SimulationPage')
def SimulationPage():
    pie_data = {
        'labels': ['Apples', 'Oranges', 'Bananas', 'Grapes'],
        'values': [50, 20, 15, 15],
        }
    return render_template('SimulationPage.html',fullname=session.get('name'), pie_data=pie_data) if not session.get('name') == None else redirect(url_for('landing'))

@app.route('/CarbonEmissionDash')
def CarbonEmissionDash():
    pie_data = {
        'labels': ['Apples', 'Oranges', 'Bananas', 'Grapes'],
        'values': [50, 20, 15, 15],
        }
    return render_template('CarbonEmissionDash.html',fullname=session.get('name'), pie_data=pie_data) if not session.get('name') == None else redirect(url_for('landing'))

@app.route('/GreenEnergyDash')
def GreenEnergyDash():
    pie_data = {
        'labels': ['Apples', 'Oranges', 'Bananas', 'Grapes'],
        'values': [50, 20, 15, 15],
        }
    return render_template('GreenEnergyDash.html',fullname=session.get('name'), pie_data=pie_data,greenenergydata=retrieve_greenenergy_data()) if not session.get('name') == None else redirect(url_for('landing'))

@app.route('/CostEstimationDash')
def CostEstimationDash():
    pie_data = {
        'labels': ['Apples', 'Oranges', 'Bananas', 'Grapes'],
        'values': [50, 20, 15, 15],
        }
    return render_template('CostEstimationDash.html',fullname=session.get('name'), pie_data=pie_data) if not session.get('name') == None else redirect(url_for('landing'))

@app.route('/AppliancesDash')
def AppliancesDash():
    pie_data = {
        'labels': ['Apples', 'Oranges', 'Bananas', 'Grapes'],
        'values': [50, 20, 15, 15],
        }
    return render_template('AppliancesDash.html',fullname=session.get('name'),pie_data=pie_data) if not session.get('name') == None else redirect(url_for('landing'))


# Google Login Route
@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url(prompt='consent')
    session["state"] = state
    return redirect(authorization_url)
    
# OAuth 2.0 Callback
@app.route("/oauth2callback")
def oauth2callback():
    global fullname, email
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
        user_record = db.find_user(table=user_table, email=email)
        print(user_record)
    
        if not user_record:
            db.add_user(table=user_table, email=email, fullname=fullname)
            return redirect(url_for("setup"))
        elif user_record[0]['hasSetup'] == 0:  # Access the first dictionary in the list
            return redirect(url_for("setup"))
        else:
            flash(f"Welcome, {session['name']}!", 'success')
            return redirect(url_for("UserDashboardContent"))

    
    except ValueError as e:
        flash("Token verification failed. Please try again.", 'error')
        return redirect(url_for("Landing"))

# Calculate Solar Panel Power Production
def calculate_weekly_powergeneration_solar(email:str):
    global panel_type,panel_quantity,weeklydata
    
    # Get User ID from email
    userid=0
    records = db.getall_users(table=user_table)
    for record in records:
        if email == record['email']:
            userid = record['id'] 

    # Calculate Solar Panel Energy Production        
    weeklydata = simulate.getTotalSolarKWH_Production(panel_type,panel_quantity)
    csv_weeklydata = ','.join(map(str, weeklydata))
    db.add_user(table='simulation', panelweekdata=csv_weeklydata,userid=userid)


def retrieve_greenenergy_data():
    email = session.get('email')
    userid = 0
    records = db.getall_users(table='user')
    for record in records:
        if record['email'] == email:
            userid = record['id']
    simulation_record = db.find_simrecord(table='simulation', userid=userid)
    simulation_record = simulation_record[0]['panelweekdata'].split(',')
    simulation_record = [float(value) for value in simulation_record]
    return simulation_record

# Dashboard Template Route
@app.route('/UserDashboardContent')
def UserDashboardContent():
    global panel_type, panel_quantity
    pie_data = {
        'labels': ['Electricity', 'Green Energy'],
        'values': [194,56],
        }

    if not session.get("name"):
        flash("Please log in first.", "error")
        return redirect(url_for('landing'))
    else:
        return render_template('UserDashboardContent.html',fullname=session.get('name'), pie_data=pie_data,kwhdata=retrieve_greenenergy_data(),days_in_week=days_in_week)

@app.route('/CostEstimation')
def CostEstimation():
    global fullname
    pie_data = {
        'labels': ['Apples', 'Oranges', 'Bananas', 'Grapes'],
        'values': [50, 20, 15, 15],
        }
    return render_template('CostEstimationDash.html',fullname=session.get('name'),pie_data=pie_data) if not session.get('name') == None else redirect(url_for('landing'))

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
    records = db.getall_users(table=user_table)
    for record in records:
        if record['email'] == email:
            return True  
    return False


# Manual Login Route
@app.route('/userlogin', methods=['POST'])
def userlogin():
    global fullname, email
    email = request.form.get('email')
    password = request.form.get('password')
    records = db.getall_users(table=user_table)
    print(records)

    # Flag to check if the account exists
    account_exists = False

    for record in records:
        if record['email'] == email:
            account_exists = True  # Account with email exists
            if record['password'] == password:
                recordname = db.find_user(table=user_table,email=email)
                print("Record Name")
                print(recordname)
                session['name'] = recordname[0]['fullname']
                session['email'] = email
                fullname = record['fullname'].split(' ')[0] + ' ' + record['fullname'].split(' ')[-1]
                flash("LOGIN SUCCESSFUL!", "info")
                return redirect(url_for('UserDashboardContent'))
            else:
                flash('Invalid Credentials!', 'error')
                return redirect(url_for('landing'))

    # If loop completes and no matching email was found
    if not account_exists:
        flash('Account does not exist!', 'error')
        return redirect(url_for('landing'))



@app.route('/userregister', methods=['POST'])
def userregister():
    global fullname, email
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    password = request.form.get('password')
    records = db.getall_users(table=user_table)
    for record in records:
        if record['email'] == email and not record['password'] == None:
            flash('Account already registered! Sign in now.', 'success')
            return redirect(url_for('landing'))
        elif record['email'] == email and record['password'] == None:
            flash('This email is already registered! Sign in using Google Accounts', 'success')
            return redirect(url_for('landing'))
    db.add_user(table=user_table,email=email,fullname=fullname, password=password)

    session['email'] = email
    session['name'] = fullname  

    flash(f"Welcome {fullname}, please complete the setup.", "success")
    return redirect(url_for('setup'))



@app.route('/submit_tariff', methods=['POST'])
def submit_tariff():
    global email, tariff_rate, tariffcompany, tariff_type
    # Retrieve JSON data from request
    data = request.get_json()
    tariffcompany = data.get('provider')
    tariff_rate = data.get('tariff_rate')
    tariff_type = data.get('tariff_type')

    # Debug print statements
    print(f"Provider: {tariffcompany}")
    print(f"Tariff Rate: {tariff_rate} kWh")
    print(f"Tariff Type: {tariff_type}")


    # Check if session['email'] is set
    if not session.get('name'):
        flash("Session expired or invalid. Please log in again.", "error")
        return jsonify({"redirect": url_for('landing')})
    hasSetup=1
    db.update_user(table='user', email=email,hasSetup=hasSetup) # This user has already setup and his hasSetup status is changed to 1
    # Calculate the solar panel generation after setup
    calculate_weekly_powergeneration_solar(email=email)

    # Confirm user session before redirecting to the dashboard
    session['registered_user'] = email  
    flash("Setup completed successfully!", "success")
    return jsonify({"redirect": url_for('UserDashboardContent')})


@app.route('/setupTariff')
def setupTariff():
    return render_template('setupTariff.html')


@app.route('/panelsetup')
def panelsetup():
    return render_template('panelsetup.html')

@app.route('/setupPanels', methods=['POST'])
def setupPanels():
    global panel_type, panel_quantity
    if request.method == 'POST':
        panel_type = request.form.get('solarpanels')
        print(panel_type)
        panel_quantity = request.form['quantity']
        print(panel_quantity)
        simulate.getTotalSolarKWH_Production(panel_type, int(panel_quantity))
    return redirect(url_for('setupTariff'))

@app.route('/setupAppliances', methods=['POST'])
def setupAppliances():
    global appliances
    if request.method == 'POST':
        appliances = request.form.getlist('mycheckbox')
        print(appliances)
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
