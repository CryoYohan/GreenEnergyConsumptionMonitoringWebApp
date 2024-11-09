from flask import Flask, render_template, redirect, url_for, request, flash, get_flashed_messages

app = Flask(__name__)

app.secret_key = '@#@#@#@'

@app.route('/userlogin', methods=['POST'])
def userlogin():
    username:str = request.form.get('username')
    password:str = request.form.get('password')
    if username == 'admin' and password == 'user':
        flash('Login Success!', 'success')
        return redirect(url_for('UserDashboardTemplate'))
    else:
        return flash(f'Invalid Credentials!\n{username} and {password}', 'error') 


@app.route('/UserDashboardTemplate')
def UserDashboardTemplate():
    return render_template('UserDashboardTemplate.html')

@app.route('/AppliancesDash')
def AppliancesDash():
    return render_template('AppliancesDash.html')

@app.route('/userreg', methods=['POST'])
def userreg():
    username:str = request.form['username']
    email:str = request.form['email']
    password:str = request.form['password']
    confirmpassword:str = request.form['confirmpassword']
    return redirect(url_for('login')) if password == confirmpassword else redirect(url_for('register'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/')
def landing():
    return render_template('Landing.html')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',port=9000)