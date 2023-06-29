from flask import Flask, render_template, request, url_for, redirect, session, send_file
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import vonage
from werkzeug.security import generate_password_hash
import time
import pandas as pd
import MySQLdb
import openpyxl



app = Flask(__name__)


client = vonage.Client(key="10d22c89", secret="tLctzKVCawSx4miG")
sms = vonage.Sms(client)

app.secret_key = "mykey"

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "learn"

mysql= MySQL(app)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/get_login', methods= ['POST', 'GET'])
def get_login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM registeration WHERE email = %s AND password = %s', (email, password))
        account  = cursor.fetchone()
        if account:
            session['logged_in'] = True
            msg="Successfully Logged In"
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect email / password !'
    return render_template('login.html', msg= msg)

@app.route('/login', methods= ['POST', 'GET'])
def login():
    if request.method== 'GET':
        return "LOGIN via Login form"

    if request.method== 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form and 'repswd' in request.form:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        repswd = request.form['repswd']

        repasword_hash = generate_password_hash(repswd)

        # checking if account exist
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM registeration WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            return "Account Already Exixt"
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return "Invalid email address!"
        elif not re.match(r'[A-Za-z]+', name):
            return "Username must contain only characters!"
        else:
            cursor= mysql.connection.cursor()
            cursor.execute(''' INSERT INTO registeration VALUES(%s,%s,%s,%s)''',(name,email,password,repasword_hash))
            mysql.connection.commit()
            cursor.close()
    return render_template('login.html')

@app.route('/find_out', methods= ['POST', 'GET'])
def find_out():
    if session.get('logged_in'):
        return render_template('find_out.html')
    else:
        return render_template('login.html')


@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/contact_farmer')
def contact_farmer():
    if session.get('logged_in'):
        return render_template('contact_farmer.html')
    else:
        return render_template('login.html')

@app.route('/send', methods= ['POST'])
def send():
    responseData = sms.send_message(
        {
        "from": "Vonage APIs",
        "to": "916266974651",
        "text": request.form.get("inputMessage"),
        }
    )

    if responseData["messages"][0]["status"] == "0":
        return "Message sent successfully."
    else:
        return "Message failed with error"

@app.route('/contact', methods= ['POST', 'GET'])
def contact():
    if request.method== 'GET':
        return "Fill the form via Home Page"
    
    if request.method== 'POST' and 'name' in request.form and 'email' in request.form and 'Message' in request.form:
        name = request.form['name']
        email = request.form['email']
        message = request.form['Message']
    
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor= mysql.connection.cursor()
        cursor.execute(''' INSERT INTO contact VALUES(%s,%s,%s)''',(name,email, message))
        mysql.connection.commit()
        cursor.close()
    return render_template('index.html')


@app.route('/logout')
def logout():
    session.clear()
    time.sleep(5)
    return redirect(url_for('form'))
    # return render_template('login.html')

@app.route('/export', methods=['GET'])
def export_data():
    # Connect to the MySQL database
    db = MySQLdb.connect(host='localhost', user='root', password='', db='learn')
    
    # Retrieve the data from the database using SQL query
    query = "SELECT * FROM registeration"
    df = pd.read_sql(query, con=db)
    db.close()
    file_path = 'file.xlsx'
    df.to_excel(file_path, index=False)

    # Return the file for download
    return send_file(file_path, as_attachment=True)

app.run(host="localhost", port=5000, debug=True)