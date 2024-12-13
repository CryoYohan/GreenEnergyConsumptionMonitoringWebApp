from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import os
from dotenv import load_dotenv
from appliances import appliances as appliancesdict
from dbhelper import Databasehelper
from simulator import Simulator
import json

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

def getfullname_with_session(session_email: str):
    # Find the user record based on email
    record = db.find_user(table=user_table, email=session_email)
    
    # Extract the 'fullname' field directly from the record
    if record and 'fullname' in record[0]:
        fullname = record[0]['fullname']
        return fullname.strip()  # Remove any extra spaces, if present
    
    # Return an empty string if no record is found or fullname is missing
    return ""


@app.route('/updateuser/<email>', methods=['POST'])
def updateuser(email):
    # Extract form data
    firstname = request.form.get('firstname', '').strip()
    lastname = request.form.get('lastname', '').strip()
    emailupdate = request.form.get('email', '').strip()
    phonenumber = request.form.get('phoneno', '').strip()
    password = request.form.get('password', '').strip()
    confirmpassword = request.form.get('confirmpassword', '').strip()

    if password != confirmpassword:
        return jsonify({'error': 'Passwords do not match!'}), 400

    # Combine firstname and lastname into fullname
    fullname = f"{firstname} {lastname}".strip() if firstname or lastname else None

    # Check if the email to be updated already exists in the database (other than the current user)
    existing_users = db.getall_users(table=user_table)
    for user in existing_users:
        if user['email'] == emailupdate and user['email'] != email:
            return jsonify({'error': 'Email already exists. Please choose a different email.'}), 400

    # Build the update dictionary dynamically
    update_data = {}
    if fullname:  # Update fullname if it exists
        update_data['fullname'] = fullname
    if emailupdate:
        update_data['email'] = emailupdate
    if phonenumber:
        update_data['phoneno'] = phonenumber
    if password:
        update_data['password'] = password

    # Perform the update only if there are fields to update
    if update_data:
        db.update_user(table=user_table, email=email, **update_data)
        return jsonify({'success': 'User details updated successfully!'}), 200
    else:
        return jsonify({'warning': 'No fields provided for update.'}), 400




@app.route('/Settings')
def Settings():
    pie_data = {
        'labels': ['Apples', 'Oranges', 'Bananas', 'Grapes'],
        'values': [50, 20, 15, 15],
        }
    user_record = db.find_user(table=user_table,email=session.get('email'))
    return render_template('Settings.html',fullname=getfullname_with_session(session.get('email')),email=session.get('email'), pie_data=pie_data,user_record=user_record) if not session.get('name') == None else redirect(url_for('landing'))

@app.route('/SimulationPage')
def SimulationPage():
    email = session.get('email')
    print(f"Email: {email}")
    pie_data = {
        'labels': ['Apples', 'Oranges', 'Bananas', 'Grapes'],
        'values': [50, 20, 15, 15],
        }
    inventory = db.getall_inventory(table='inventory',email=email)
    return render_template('SimulationPage.html',fullname=getfullname_with_session(session.get('email')), pie_data=pie_data,inventory=inventory) if not session.get('name') == None else redirect(url_for('landing'))

@app.route('/CarbonEmissionDash')
def CarbonEmissionDash():
    pie_data = {
        'labels': ['Apples', 'Oranges', 'Bananas', 'Grapes'],
        'values': [50, 20, 15, 15],
        }
    sum_carbonemission = round(sum(retrieve_carbonemissions()),2)
    sum_carbonemissiongreen = round(sum(retrieve_carbonemissions_greenenergy()),2)
    deducted_carbonemission = round((sum_carbonemission - sum_carbonemissiongreen),2)

    return render_template('CarbonEmissionDash.html',fullname=getfullname_with_session(session.get('email')), 
                           pie_data=pie_data,carbonemission=retrieve_carbonemissions(),
                           carbonemissiongreen=retrieve_carbonemissions_greenenergy(),
                           sum_carbonemission=sum_carbonemission,
                           sum_carbonemissiongreen=sum_carbonemissiongreen,
                           deducted_carbonemission=deducted_carbonemission
                           ) if not session.get('name') == None else redirect(url_for('landing'))

@app.route('/GreenEnergyDash')
def GreenEnergyDash():
    pie_data = {
        'labels': ['Apples', 'Oranges', 'Bananas', 'Grapes'],
        'values': [50, 20, 15, 15],
        }
    greenenergydata = retrieve_greenenergy_data()
    sum_greenenergydata = round(sum(greenenergydata),2)
    return render_template('GreenEnergyDash.html',fullname=getfullname_with_session(session.get('email')), pie_data=pie_data,greenenergydata=greenenergydata,sum_greenenergydata=sum_greenenergydata)if not session.get('name') == None else redirect(url_for('landing'))

@app.route('/CostEstimationDash')
def CostEstimationDash():
    pie_data = {
        'labels': ['Apples', 'Oranges', 'Bananas', 'Grapes'],
        'values': [50, 20, 15, 15],
        }
    return render_template('CostEstimationDash.html',fullname=getfullname_with_session(session.get('email')), pie_data=pie_data) if not session.get('name') == None else redirect(url_for('landing'))

@app.route('/AppliancesDash')
def AppliancesDash():
    appliances_sorted_consumption_data = retrieve_sortedappliances_consumption()
    sum_appliances_consumption = round(sum(retrieve_kwhconsumption_data()),2)
    return render_template('AppliancesDash.html',fullname=getfullname_with_session(session.get('email')),
                           appliances_sorted_consumption_data=appliances_sorted_consumption_data,
                           sum_appliances_consumption=sum_appliances_consumption
                           ) if not session.get('name') == None else redirect(url_for('landing'))


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
            return redirect(url_for("UserDashboardContent"))

    
    except ValueError as e:
        flash("Token verification failed. Please try again.", 'error')
        return redirect(url_for("Landing"))

# Calculate Total Power Consumption of Appliances
def calculate_total_consumption(appliances:list,email:str):
    # Get User ID from email
    userid=0
    records = db.getall_users(table=user_table)
    for record in records:
        if email == record['email']:
            userid = record['id'] 

    # Calculate Solar Panel Energy Production        
    kwhconsumption:list = simulate.getTotalConsumption(appliances=appliances)
    csv_kwhconsumption:str = ','.join(map(str, kwhconsumption))
    print('JOINED KWHCONSUMPTION')
    print(csv_kwhconsumption)
    db.update_user(table='simulation', userid=userid,kwhconsumption=csv_kwhconsumption)

def calculate_total_consumption_sorted(appliances:list,email:str):
    # Get User ID from email
    userid=0
    records = db.getall_users(table=user_table)
    for record in records:
        if email == record['email']:
            userid = record['id'] 

    # Calculate Solar Panel Energy Production        
    kwhconsumption_sorted = simulate.getTotalConsumption2(appliances=appliances)
    # Convert to JSON string
    json_data = json.dumps(kwhconsumption_sorted)
    print('JOINED KWHCONSUMPTION')
    print(kwhconsumption_sorted)
    db.update_user(table='simulation', userid=userid,appliance_consumption=json_data)


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
    db.update_user(table='simulation',userid=userid, panelweekdata=csv_weeklydata)

# Calculate KWH Consumption Equivalent Cost in Pesos
def calculate_total_consumption_equivalent_cost(email:str,totalConsumption:list, tariffRate:str, tariffType:str):
     # Get User ID from email
    userid=0
    records = db.getall_users(table=user_table)
    for record in records:
        if email == record['email']:
            userid = record['id'] 
            
    weeklycost = simulate.getTotalCosts(totalConsumption=totalConsumption,tariffRate=tariffRate,tariffType=tariffType)
    csv_weeklycost =','.join(map(str, weeklycost))
    db.update_user(table='simulation', userid=userid,costofkwh=csv_weeklycost)

# Calculate KWH Consumption Equivalent Cost in Pesos with Green Energy
def calculate_total_consumption_equivalent_cost_with_greenenergy(email:str,totalConsumption:list,totalGreenEnergy:list, tariffRate:str, tariffType:str)->None:
     # Get User ID from email
    userid=0
    records = db.getall_users(table=user_table)
    for record in records:
        if email == record['email']:
            userid = record['id'] 
            
    weeklycost_with_greenenergy = simulate.getTotalCostwithGreenEnergy(totalConsumption=totalConsumption,totalGreenEnergy=totalGreenEnergy,tariffRate=tariffRate,tariffType=tariffType)
    csv_weeklycost_with_greenenergy =','.join(map(str, weeklycost_with_greenenergy))
    db.update_user(table='simulation', userid=userid,costofkwhgreen=csv_weeklycost_with_greenenergy)

# Calculate the carbon emission of KWH consumption according to each Tariff Companies
def calculate_carbon_emission(email:str,totalConsumption:list,tariff_company:str):
      # Get User ID from email
    userid=0
    records = db.getall_users(table=user_table)
    for record in records:
        if email == record['email']:
            userid = record['id'] 
            
    weekly_carbonemission = simulate.getTotalCarbonEmissions(totalConsumption=totalConsumption,tariff_company=tariff_company)
    csv_weekly_carbonemission=','.join(map(str, weekly_carbonemission))
    print(f"WEEKLY CARBON EMISSION: {csv_weekly_carbonemission}")
    db.update_user(table='simulation', userid=userid,carbonemission=csv_weekly_carbonemission)

# Calculate the carbon emission of KWH consumption according to each Tariff Companies with Green Energy
def calculate_carbon_emission_green(email:str,totalConsumption:list,totalGreenEnergy:list,tariff_company:str):
      # Get User ID from email
    userid=0
    records = db.getall_users(table=user_table)
    for record in records:
        if email == record['email']:
            userid = record['id'] 

    deducted_weekly_consumption = simulate.deductkwhFromGreenEnergy(totalConsumption=totalConsumption,totalGreenEnergy=totalGreenEnergy)
    weekly_carbonemissiongreen = simulate.getTotalCarbonEmissions(totalConsumption=deducted_weekly_consumption,tariff_company=tariff_company)
    csv_weekly_carbonemissiongreen=','.join(map(str, weekly_carbonemissiongreen))
    print(f"WEEKLY CARBON EMISSION with Green Energy: {csv_weekly_carbonemissiongreen}")
    db.update_user(table='simulation', userid=userid,carbonemissiongreen=csv_weekly_carbonemissiongreen)

def retrieve_kwhconsumption_data():
    email = session.get('email')
    userid = 0
    records = db.getall_users(table='user')
    for record in records:
        if record['email'] == email:
            userid = record['id']
    simulation_record = db.find_simrecord(table='simulation', userid=userid)
    simulation_record = simulation_record[0]['kwhconsumption'].split(',')
    simulation_record = [float(value) for value in simulation_record]
    return simulation_record

def retrieve_sortedappliances_consumption():
    email = session.get('email')    
    userid = 0
    records = db.getall_users(table='user')
    for record in records:
        if record['email'] == email:
            userid = record['id']
    result = db.find_simrecord(table='simulation', userid=userid)
    print('RESULT JSON')
    print(result)
    appliance_consumption = json.loads(result[0]['appliance_consumption'])
    print('LOADED JSON')
    print(appliance_consumption)
    return appliance_consumption

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

def retrieve_costkwh():
    email = session.get('email')
    userid = 0
    records = db.getall_users(table='user')
    for record in records:
        if record['email'] == email:
            userid = record['id']
    simulation_record = db.find_simrecord(table='simulation', userid=userid)
    simulation_record = simulation_record[0]['costofkwh'].split(',')
    simulation_record = [float(value) for value in simulation_record]
    return simulation_record


def retrieve_costkwhgreen():
    email = session.get('email')
    userid = 0
    records = db.getall_users(table='user')
    for record in records:
        if record['email'] == email:
            userid = record['id']
    simulation_record = db.find_simrecord(table='simulation', userid=userid)
    simulation_record = simulation_record[0]['costofkwhgreen'].split(',')
    simulation_record = [float(value) for value in simulation_record]
    return simulation_record

def retrieve_carbonemissions():
    email = session.get('email')
    userid = 0
    records = db.getall_users(table='user')
    for record in records:
        if record['email'] == email:
            userid = record['id']
    simulation_record = db.find_simrecord(table='simulation', userid=userid)
    simulation_record = simulation_record[0]['carbonemission'].split(',')
    simulation_record = [float(value) for value in simulation_record]
    return simulation_record

def retrieve_carbonemissions_greenenergy():
    email = session.get('email')
    userid = 0
    records = db.getall_users(table='user')
    for record in records:
        if record['email'] == email:
            userid = record['id']
    simulation_record = db.find_simrecord(table='simulation', userid=userid)
    simulation_record = simulation_record[0]['carbonemissiongreen'].split(',')
    simulation_record = [float(value) for value in simulation_record]
    return simulation_record

# Dashboard Template Route
@app.route('/UserDashboardContent')
def UserDashboardContent():
    global panel_type, panel_quantity
    sum_green_data = round(sum(retrieve_greenenergy_data()),2)
    sum_total_consumption = sum(retrieve_kwhconsumption_data())
    sum_total_carbonemission = round(sum(retrieve_carbonemissions()),2)
    sum_total_carbonemissiongreen = round(sum(retrieve_carbonemissions_greenenergy()),2)
    appliances_sorted_consumption_data = retrieve_sortedappliances_consumption()
    pie_data = {
        'labels': ['Electricity in KWH', 'Green Energy in KWH'],
        'values': [sum_total_consumption,sum_green_data],
        }

    if not session.get("name"):
        flash("Please log in first.", "error")
        return redirect(url_for('landing'))
    else:
        return render_template('UserDashboardContent.html',
                               fullname=getfullname_with_session(session.get('email')), 
                               pie_data=pie_data,
                               appliances_sorted_consumption_data=appliances_sorted_consumption_data,
                               kwhdata=retrieve_greenenergy_data(),days_in_week=days_in_week,
                               carbonemission=retrieve_carbonemissions(),
                               carbonemissiongreen=retrieve_carbonemissions_greenenergy(),
                               sum_total_carbonemission=sum_total_carbonemission,
                               sum_total_carbonemissiongreen=sum_total_carbonemissiongreen,
                               sum_green_data=sum_green_data,
                               )

@app.route('/CostEstimation')
def CostEstimation():
    sum_cost_kwh = round(sum(retrieve_costkwh(),2))
    sum_cost_kwh_green = round(sum(retrieve_costkwhgreen(),2))
    deducted_sum_costkwh = sum_cost_kwh - sum_cost_kwh_green
    pie_data = {
        'labels': ['Apples', 'Oranges', 'Bananas', 'Grapes'],
        'values': [50, 20, 15, 15],
        }
    costkwh = retrieve_costkwh()
    costkwhgreen = retrieve_costkwhgreen()
    return render_template('CostEstimationDash.html',fullname=getfullname_with_session(session.get('email')),
                           pie_data=pie_data,costkwh=costkwh,costkwhgreen=costkwhgreen,sum_cost_kwh=sum_cost_kwh,
                           sum_cost_kwh_green=sum_cost_kwh_green, deducted_sum_costkwh=deducted_sum_costkwh) if not session.get('name') == None else redirect(url_for('landing'))

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
        if email == record['email'] and email == 'kryllosadmin':
            if password == record['password']:
                recordname = db.find_user(table=user_table,email=email)
                session['name'] = recordname[0]['fullname']
                session['email'] = email
                fullname = record['fullname'].split(' ')[0] + ' ' + record['fullname'].split(' ')[-1]
                return redirect(url_for('AdminDashboard'))
        elif record['email'] == email:
            account_exists = True  # Account with email exists
            if record['password'] == password:
                recordname = db.find_user(table=user_table,email=email)
                session['name'] = recordname[0]['fullname']
                session['email'] = email
                fullname = record['fullname'].split(' ')[0] + ' ' + record['fullname'].split(' ')[-1]
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
    return redirect(url_for('setup'))



@app.route('/submit_tariff', methods=['POST'])
def submit_tariff():
    global email, tariff_rate, tariffcompany, tariff_type,appliances,panel_type,panel_quantity
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

    userid=0
    records = db.getall_users(table=user_table)
    for record in records:
        if email == record['email']:
            userid = record['id'] 
    hasSetup=1
    # Set the user status to Has SETUP
    db.update_user(table='user', email=email,hasSetup=hasSetup) # This user has already setup and his hasSetup status is changed to 1
    # Add this user to Simulation Table
    db.add_user(table='simulation', userid=userid) 
    # Calculate Total KWH Consumption of Appliances
    calculate_total_consumption(appliances=appliances, email=email)
    # Calculate the Total KWH of each type of appliances
    calculate_total_consumption_sorted(appliances=appliances, email=email)
    # Calculate the solar panel generation after setup
    calculate_weekly_powergeneration_solar(email=email)
    # Calculate the cost according to the tariff rate
    calculate_total_consumption_equivalent_cost(email=email, totalConsumption=retrieve_kwhconsumption_data(),tariffRate=tariff_rate, tariffType=tariff_type)
    print(f"LIST OF KWH CONSUMPTION {retrieve_kwhconsumption_data()}")
    # Calculate the cost of kwh consumption, deducted by Green Energy
    calculate_total_consumption_equivalent_cost_with_greenenergy(email=email, totalConsumption=retrieve_kwhconsumption_data(),totalGreenEnergy=retrieve_greenenergy_data(),tariffRate=tariff_rate, tariffType=tariff_type)
    # Calculate Carbon Emission
    calculate_carbon_emission(email=email,totalConsumption=retrieve_kwhconsumption_data(),tariff_company=tariffcompany)
    # Calculate Carbon Emission
    calculate_carbon_emission_green(email=email,totalConsumption=retrieve_kwhconsumption_data(),totalGreenEnergy=retrieve_greenenergy_data(),tariff_company=tariffcompany)
    # Insert appliance, solar, and user data in inventory table
    insert_to_inventory(userid=userid,email=email,appliances=appliances,panel_type=panel_type,
                        panel_quantity=panel_quantity,tariffcompany=tariffcompany,
                        tariffrate=tariff_rate,tarifftype=tariff_type)

    
    # Confirm user session before redirecting to the dashboard
    session['registered_user'] = email  
    return jsonify({"redirect": url_for('loader')})

@app.route('/loader')
def loader():
    return render_template('loader.html',fullname=session.get('name')) if not session.get('name') == None else redirect(url_for('landing'))
    
@app.route('/UserManagement')
def UserManagement():
    records = db.getall_joinedrecords()
    return render_template('AdminCarbonEmissionDash.html',fullname=session.get('name'),records=records) if not session.get('name') == None else redirect(url_for('landing'))

@app.route('/AdminDashboard')
def AdminDashboard():
    tariffstats = [
        len(db.getall_tariffcompanystats('tariffcompany','MERALCO')),
        len(db.getall_tariffcompanystats('tariffcompany','VECO')),
        len(db.getall_tariffcompanystats('tariffcompany','CEBECO')),
        len(db.getall_tariffcompanystats('tariffcompany','TORECO')),
        len(db.getall_tariffcompanystats('tariffcompany','Aboitiz'))
    ]

    panelstats = [
        len(db.getall_tariffcompanystats('panelname','monocrystalline')),
        len(db.getall_tariffcompanystats('panelname','polycrystalline')),
        len(db.getall_tariffcompanystats('panelname','thin-film')),
    ]

    return render_template('AdminDashboardContent.html',fullname=session.get('name'),tariffstats=tariffstats,panelstats=panelstats) if not session.get('name') == None else redirect(url_for('landing'))

def insert_to_inventory(userid,email, appliances: list, panel_type, panel_quantity,tariffcompany,tariffrate,tarifftype):
    # Fetch all appliances and panel details from the database
    appliances_db = db.getall_users(table='appliance')  # All appliances
    panelrecord = db.find_panel(table='solarpanel', panelname=panel_type)  # Panel details
    
    if not panelrecord:
        raise ValueError(f"No panel found with the type: {panel_type}")
    
    # Create a mapping of appliance names to their records for faster lookup
    appliance_map = {appl['appliancename']: appl for appl in appliances_db}
    
    # Iterate through the appliances provided in the list
    for appliance in appliances:
        # Check if the appliance exists in the database
        if appliance in appliance_map:
            appliance_record = appliance_map[appliance]
            # Insert the appliance into the inventory table
            db.add_user(
                table='inventory',
                userid=userid,
                email=email,
                applianceid=appliance_record['applianceid'],
                appliancename=appliance_record['appliancename'],
                watt=appliance_record['watt'],
                panel_id=panelrecord[0]['panel_id'],
                hours_use=panelrecord[0]['hours_use'],
                wattcapacity=panelrecord[0]['wattcapacity'],
                panelname=panel_type,
                panel_quantity=panel_quantity,
                tariffcompany=tariffcompany,
                tariffrate=tariffrate,
                tarifftype=tarifftype
            )
        else:
            print(f"Appliance '{appliance}' not found in the database, skipping.")


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
