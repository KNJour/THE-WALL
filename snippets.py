

@app.route('/login_user', methods=['POST'])
def login_user():
    query = "SELECT * FROM users WHERE email = %(email)s"data = {
        email
    }
    mysql = connectToMySQL("users")
    result = mysql.query_db(query,data)
    if len(result) >0:
        if bycrypt.check_password_hash(result[0]['password'], request.form['password']):
            session['user_id'] = result [0]['id']
            return redirect('/success')
        else:
            flash("Password does not match")
    else:
        flash("Could not Login!")