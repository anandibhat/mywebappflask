from flask import Flask, render_template, request, redirect, session
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import id_token
from google.auth.transport import requests

# Set up the Google Sheets API credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Open the Google Sheets worksheet
sheet = client.open('myproject').sheet1

# Set up the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Google Sign-In client ID and redirect URI
CLIENT_ID = '718039634792-9v2ql0jog1sqoacgujg0cp9luvn5gg1d.apps.googleusercontent.com'
REDIRECT_URI = 'http://localhost:5000/google-signin'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        # Insert the user data into the Google Sheets worksheet
        row = [name, email, password]
        sheet.insert_row(row, index=2)
        # Set the user session data
        session['name'] = name
        session['email'] = email
        return redirect('/dashboard')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Check if the user exists in the Google Sheets worksheet
        rows = sheet.get_all_values()
        for row in rows:
            if row[1] == email and row[2] == password:
                # Set the user session data
                session['name'] = row[0]
                session['email'] = row[1]
                # Log the user login details in the Google Sheets worksheet
                log_row = [row[0], row[1], 'Login']
                sheet.insert_row(log_row, index=2)
                return redirect('/dashboard')
        return render_template('login.html', error='Invalid email or password.')
    return render_template('login.html')
@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        return render_template('dashboard.html', name=session['name'], email=session['email'])
    else:
        return redirect('/login')

@app.route('/google-login', methods=['POST'])
def google_login():
    token = request.form['idtoken']
    try:
        # Verify the Google Sign-In token
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        email = idinfo['email']
        print('Google Sign-In: email =', email)
        # Check if the user exists in the Google Sheets worksheet
        rows = sheet.get_all_values()
        for row in rows:
            if row[1] == email:
                # Set the user session data
                session['name'] = row[0]
                session['email'] = row[1]
                print('Google Sign-In: existing user found:', row[0])
                return redirect('/dashboard')
        # If the user is not found in the worksheet, sign them up
        name = idinfo['name']
        row = [name, email, '']
        sheet.insert_row(row, index=2)
        # Set the user session data
        session['name'] = name
        session['email'] = email
        # Log the user sign-up details in the Google Sheets worksheet
        log_row = [name, email, 'Google Sign-Up']
        sheet.insert_row(log_row, index=2)
        print('Google Sign-In: new user signed up:', name)
        return redirect('/dashboard')
    except ValueError:
        # Invalid token
        print('Google Sign-In: invalid token')
        return redirect('/login')

       

       





