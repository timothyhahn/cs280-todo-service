from todo import app, login_manager
from flask.ext.login import login_required, login_user, current_user
from flask import url_for, redirect, request, jsonify
from database import db_session
from models import Task, User
from datetime import datetime


# API
## GET

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)


@app.route('/task', methods=['GET'])
@login_required
def get_all_tasks():
    tasks = Task.query.filter(Task.user_id == current_user.id)
    tasks_dict = dict()
    tasks_list = list()
    for task in tasks:
        tasks_list.append(task.info())
    tasks_dict['tasks'] = tasks_list
    return jsonify(tasks_dict)


@app.route('/task/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return "Task does not exist"
    if task.user_id != current_user.id:
        return "You do not own this task"

    return jsonify(task.info())


@app.route('/task', methods=['POST'])
@login_required
def add_new_task():
    user_id = current_user.id
    description = request.form['description']
    notes = request.form['notes']
    longitude = request.form['longitude']
    latitude = request.form['latitude']
    attachment = request.form['attachment']
    category_id = request.form['category_id']
    if request.form['due_date'] == '':
        due_date = None
    else:
        due_date = datetime.strptime(request.form['due_date'], "%b %d %Y")

    task = Task(user_id=user_id, description=description, notes=notes, due_date=due_date, longitude=longitude, latitude=latitude, attachment=attachment, category_id=category_id)
    db_session.add(task)
    db_session.commit()
    return jsonify(task.info())


@app.route('/task/<int:task_id>', methods=['POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return "Task does not exist"
    if task.user_id != current_user.id:
        return "You do not own this task"

    task.description = request.form['description']
    task.notes = request.form['notes']
    if request.form['complete'] == 'true':
        task.complete = True
    else:
        task.complete = False
    task.latitude = request.form['latitude']
    task.longitude = request.form['longitude']
    task.category = request.form['category']
    task.attachment = request.form['attachment']
    if request.form['due_date'] == '':
        due_date = None
    else:
        due_date = datetime.strptime(request.form['due_date'], "%b %d %Y")

    db_session.commit()
    return jsonify(task.info())


@app.route('/task/delete/<int:task_id>', methods=['POST', 'DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return "Task does not exist"
    if task.user_id != current_user.id:
        return "You do not own this task"
    db_session.delete(task)
    db_session.commit()
    return 'Successfully deleted'


@app.route('/login', methods=['POST'])
def login():
    username = request.authorization['username']
    password = request.authorization['password']
    user = User.query.filter(User.username == username).first()
    if not user or not user.is_valid(password):
        return 'Invalid credentials'
    login_user(user)
    return 'hi'


@app.route('/register', methods=['POST'])
def register():
    username = request.authorization['username']
    password = request.authorization['password']
    user = User.query.filter(User.username == username).first()
    if user:
        return 'User already exists'
    user = User(username=username, password=password)
    db_session.add(user)
    db_session.commit()
    login_manager.login_user(user)
    return 'hi'


# TURN OFF DB
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
