from flask import render_template, jsonify, redirect, url_for, current_app
from flask_jwt_extended import create_access_token
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
from flask import session

from main import main 


class LoginForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired('cannot be null'),
                                                 Length(max=10, min=3, message='name should be 3-10 lengths')])
    password = PasswordField(label='Password', validators=[DataRequired('cannot be null'), Length(max=10, min=3,
                                                                                                  message='passwd should be 3-10 lengths')])
    submit = SubmitField(label='submit')

class RegistrationForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired('cannot be null'),
                                                         Length(max=10, min=3, message='Username should be 3-10 characters long')])
    password = PasswordField(label='Password', validators=[DataRequired('cannot be null'), Length(max=10, min=3,
                                                                                                  message='Password should be 3-10 characters long')])
    submit = SubmitField(label='Register')

@main.route('/login', methods=['GET', 'POST'])
def login():
    mongo = current_app.mongo
    bcrypt = current_app.bcrypt
    form = LoginForm()
    if form.validate_on_submit():
        username = form.name.data
        password = form.password.data
        
        user = mongo.db.users.find_one({"username": username})
        
        if user and bcrypt.check_password_hash(user["password"], password):
            access_token = create_access_token(identity=username)
            session['logged_in'] = True
            session['token'] = access_token
            return redirect(url_for('main.index'))
    return render_template('login.html', form=form)

@main.route("/logout")
def logout():
    session.pop('logged_in')
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    mongo = current_app.mongo
    bcrypt = current_app.bcrypt
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check if user already exists
        existing_user = mongo.db.users.find_one({"username": username})
        if existing_user:
            return jsonify(message="Username already exists!"), 400

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        mongo.db.users.insert_one({"username": username, "password": hashed_password})
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main.route('/')
def index():
    if session.get("logged_in"):
        return render_template('index.html')
    else:
        return redirect(url_for('main.login'))
       

