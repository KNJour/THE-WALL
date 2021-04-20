from flask import Flask, render_template, request,session,redirect, flash
from mysqlconnection  import connectToMySQL
from flask_bcrypt import Bcrypt
import re
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "Benny Bob wuz heer."

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')
#REGISTRATION
@app.route('/register', methods=['POST'])
def submit():
    session.clear()
    is_valid = True
    coolquery = "SELECT * FROM users"
    email_list = connectToMySQL("the_wall").query_db(coolquery)
    for one in email_list:
        if one['email'] == request.form['email']:
            is_valid = False
            flash("EMAIL IS ALREADY TAKEN", "register")
    if len(request.form['first_name']) < 2:
        is_valid = False
        flash("**Please enter a first name**", "register")
    if not NAME_REGEX.match(request.form['first_name']):
        is_valid = False
        flash("**MUST BE FIRST NAME LETTERS ONLY**", "register")
    if len(request.form['last_name']) < 1:
        is_valid = False
        flash("Please enter a last name", "register")
    if not NAME_REGEX.match(request.form['last_name']):
        is_valid = False
        flash("**MUST BE LETTERS ONLY**", "register")
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Invalid email address!", "register")
    if len(request.form['password']) < 8:
        is_valid = False
        flash("Please enter a password with at least 8 characters", "register")
    if (request.form['password'] != request.form['confirm_password']):
        is_valid = False
        flash("Passwords Do Not Match", "register")

    if not is_valid:
        return redirect ('/')

    else:
        flash("Registration Successful!", "register")
        hashedPass = bcrypt.generate_password_hash(request.form['password'])

        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(first_name)s,%(last_name)s,%(email)s, %(password)s,NOW(),NOW());"

        print(query)
        data = {
            'first_name' : request.form['first_name'],
            'last_name' : request.form['last_name'],
            'email' : request.form['email'],
            'password' : hashedPass
            }
        users = connectToMySQL("the_wall").query_db(query, data)
        print(users)
        
        return redirect ('/')
#LOGIN
@app.route('/login', methods=['POST'])
def login():
    query = "SELECT * FROM users WHERE users.email = %(email)s"
    data = {
        'email' : request.form['email_check']
    }
    hashedPass = request.form['password_check']
    
    user = connectToMySQL("the_wall").query_db(query, data)
    print("HEHEEERERERERERERERERERERERERRERERER")
    print(user)
    if len(user) < 1:
        flash("invalid email", "login")
        return redirect('/')

    if bcrypt.check_password_hash(user[0]["password"], hashedPass):
        session['first_name'] = user[0]["first_name"]
        session['last_name'] = user[0]["last_name"]
        session['id'] = user[0]["id"]
        return redirect('/login_successful')
    else:
        flash("password is incorrect", "login")
        return redirect('/')
#DELETE

@app.route('/delete', methods=['POST'])
def delete ():
    query = "DELETE FROM messages WHERE content = %(message)s;"
    data = {
        "message" : request.form['message']
    }
    deleted = connectToMySQL("the_wall").query_db(query, data)
    flash("DELETED")
    return redirect ('/login_successful')


@app.route('/login_successful')
def login_success():
    query = "SELECT * FROM users WHERE id != %(id)s;"
    messagequery = "SELECT * FROM users JOIN messages ON messages.reciever_id = %(id)s AND messages.sender_id = users.id;"
    sentquery = "SELECT * FROM messages WHERE sender_id = %(id)s;"
    data = {
        "id" : session['id']
    }
    sent = connectToMySQL("the_wall").query_db(sentquery, data)
    sentamount = len(sent)
    messages = connectToMySQL("the_wall").query_db(messagequery, data)
    users = connectToMySQL("the_wall").query_db(query, data)
    print('CHECK')
    amount = len(messages)
    print (messages)
    print(amount)
    return render_template('the_wall.html', users = users, messages = messages, amount = amount, sentamount = sentamount)

#LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')


@app.route('/')
def homePage():
    return render_template("register.html")

##SEND MESSAGE
@app.route("/send_message", methods=['POST'])
def send_message():
    query = "INSERT INTO messages (content, created_at, updated_at, sender_id, reciever_id) VALUES (%(message)s, NOW(), NOW(), %(sender)s, %(reciever)s);"
    print(query)
    data = {
        "message" : request.form['message'],
        "sender" : session['id'],
        "reciever" : request.form['id']
    }
    message = connectToMySQL("the_wall").query_db(query,data)
   
    print(data)
    flash("Message Sent!")

    return redirect('/login_successful')

if __name__=="__main__":
    app.run(debug=True)