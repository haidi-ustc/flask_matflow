import os
import json
import markdown
from flask import session
from bson import ObjectId
from flask import render_template, jsonify, redirect, url_for, current_app, request,flash
from flask_jwt_extended import create_access_token
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
from datetime import datetime

from main import main 


class LoginForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired('cannot be null'),
                                                 Length(max=10, min=3, message='name should be 3-10 lengths')])
    password = PasswordField(label='Password', validators=[DataRequired('cannot be null'), Length(max=10, min=3,
                                                                                                  message='passwd should be 3-10 lengths')])
    submit = SubmitField(label='Login')

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
    # Read the README.md file
    with open(os.path.dirname(main.root_path) + '/README.md', 'r') as f:
        content = f.read()

    # Convert to HTML
    content_html = markdown.markdown(content)

    return render_template('index.html', content=content_html)

@main.route('/list_projects')
def list_projects():
    mongo = current_app.mongo
    projects=list(mongo.db.projects.find().sort("created_time", -1))
    if session.get("logged_in"):
        return render_template('list_projects.html',projects=projects)
    else:
        return redirect(url_for('main.index'))

@main.route('/create_project', methods=['GET'])
def create_project():
    if session.get("logged_in"):
       return render_template('create_project.html')
    else:
        return redirect(url_for('main.index'))

@main.route('/save_project', methods=['POST'])
def save_project():
    mongo = current_app.mongo
    title = request.form.get('title')
    description = request.form.get('description')
    if 'dagFile' in request.files and request.files['dagFile'].filename != '':
        dag_file = request.files['dagFile']
        dag_str = dag_file.read().decode('utf-8')
    else:
        dag_str = request.form.get('dag')
    dag = json.loads(dag_str)

    entry = mongo.db.projects.insert_one({"title":title,
                       "description":description,"dag":dag,
                       "created_time":datetime.now(),"ended_time":None})
    if entry.inserted_id:
       flash('Project saved successfully!', 'success')
       return redirect(url_for('main.list_projects'))
    else:
       flash('Project saved Failed!', 'fail')
       return render_template('create_project.html')

@main.route('/update_project_dag', methods=['POST'])
def update_project_dag():
    mongo = current_app.mongo
    project_id = ObjectId(request.form.get('project_id'))
    dag_data = json.loads(request.form.get('dag_data'))

    project = mongo.db.projects.find_one({"_id": project_id})
    if project:
        mongo.db.projects.update_one({"_id": project_id}, {"$set": {"dag": dag_data}})
        return jsonify({"message": "Data updated successfully!"})
    else:
        return jsonify({"message": "Project not found!"}), 404
