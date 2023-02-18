import os

from flask import Flask, abort
from flask import render_template
from flask import redirect
from flask import request
from flask import session
from . import db

app = Flask(__name__)
app.secret_key = b'f01790380dc11025fcc4c8008d127a3b9da5f20199ce85efbd4bab36f68bd43d'


app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, 'tourdeflask.sqlite'),
)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

db.init_app(app)


@app.route('/', methods=['POST', 'GET'])
def all_log_list():  # put application's code here
    if request.method == 'POST':
        user_or_mail = request.form.get('user_or_mail', type=str)
        password = request.form.get('password', type=str)
        user = db.user_auth(user_or_mail, password)
        if type(user) is db.User:
            session["user_id"] = user.user_id
            session["username"] = user.username
            session["admin"] = user.admin
        else:
            abort(400, user)
    if 'user_id' in session:
        print(session['user_id'])
        dev_logs = db.select_dev_logs(session["user_id"])
        log = []
        langs = db.list_langs()
        return render_template('log_list.html', dev_logs=dev_logs, log=log, langs=langs)
    return redirect('/login')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('bool_admin', None)
    return redirect('/')


@app.route('/delete_dev/<int:developer_id>')
def dev_delete(developer_id):
    db.delete_dev(developer_id)
    return redirect('/devs')


@app.route('/devs')
def dev_form():  # put application's code here
    if not session['admin']:
        return redirect('/')
    devs = db.select_all_users()
    log = []
    langs = db.list_langs()
    return render_template('dev_list.html', devs=devs, log=log, langs=langs)


@app.route('/create_dev', methods=['POST', 'GET'])
def dev_insert():  # put application's code here
    if request.method == 'POST':
        new_name = request.form.get('new_name', type=str)
        if new_name != '':
            result = db.insert_dev(new_name)
            if result == 'Error':
                abort(400, 'Name already exists.')
    return redirect('/devs')


@app.route('/edit_dev/<int:developer_id>', methods=['POST', 'GET'])
def dev_edit(developer_id):  # put application's code here
    if request.method == 'POST':
        new_name = request.form.get('new_name', type=str)
        result = db.update_dev(developer_id, new_name)
        if result == 'Error':
            abort(400, 'Name already exists.')
    return redirect('/devs')


@app.route('/new/All', methods=['POST', 'GET'])
def log_form():  # put application's code here
    if request.method == 'POST':
        name = request.form.get('dev', type=str)
        work_date = request.form.get('work_date', type=str)
        lang = request.form.get('lang', type=str)
        duration = request.form.get('duration', type=int)
        rating = request.form.get('rating', type=int)
        note = request.form.get('note', type=str)
        result = db.insert_log(name, work_date, lang, duration, rating, note)
        if result == 'Error':
            abort(400, 'Developer does not exist.')
    return redirect('/')


@app.route('/dev/new/<int:dev_id>', methods=['POST', 'GET'])
def dev_log_form(dev_id):  # put application's code here
    if request.method == 'POST':
        name = request.form.get('dev', type=str)
        work_date = request.form.get('work_date', type=str)
        lang = request.form.get('lang', type=str)
        duration = request.form.get('duration', type=int)
        rating = request.form.get('rating', type=int)
        note = request.form.get('note', type=str)
        result = db.insert_log(name, work_date, lang, duration, rating, note)
        if result == 'Error':
            abort(400, 'Developer does not exist.')
    return redirect('/dev/' + str(dev_id))


@app.route('/delete_log/<int:log_id>')
def log_delete(log_id):
    db.delete_log(log_id)
    return redirect('/')


@app.route('/dev/delete_log/<int:log_id>')
def dev_log_delete(log_id):
    log = db.select_one_log(log_id)
    dev_id = log['developer_id']
    db.delete_log(log_id)
    return redirect('/dev/' + str(dev_id))


@app.route('/edit_log/<int:log_id>')
def log_update_form(log_id):
    langs = db.list_langs()
    devs = db.select_all_users()
    log = db.select_one_log(log_id)
    return render_template('edit_log_form.html', devs=devs, langs=langs, log=log)


@app.route('/edit/<int:log_id>', methods=['POST', 'GET'])
def log_update(log_id):
    dev_id = ''
    if request.method == 'POST':
        name = request.form.get('dev', type=str)
        work_date = request.form.get('work_date', type=str)
        lang = request.form.get('lang', type=str)
        duration = request.form.get('duration', type=int)
        rating = request.form.get('rating', type=int)
        note = request.form.get('note', type=str)
        result = db.update_log(log_id, name, work_date, lang, duration, rating, note)
        dev_id = str(db.dev_name_to_id(name))
        if result == 'Error':
            abort(400, 'Developer or log does not exist.')
    return redirect('/dev/' + dev_id)


if __name__ == '__main__':
    app.run()
