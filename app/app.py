import os

from flask import Flask, abort
from flask import render_template
from flask import redirect
from flask import request
from . import db

app = Flask(__name__)

app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, 'tourdeflask.sqlite'),
)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

db.init_app(app)


@app.route('/')
def all_log_list():  # put application's code here
    for_dev = request.args.get('dev', 'All')
    all_logs = db.select_all_logs()
    devs = db.select_all_devs()
    return render_template('log_list.html', all_logs=all_logs, devs=devs, for_dev=for_dev)


@app.route('/test/<int:developer_id>')
def dev_update(developer_id):  # put application's code here
    developer_id = 1
    new_name = 'penis'
    db.update_dev(developer_id, new_name)
    return redirect('/devs')


@app.route('/dev/<int:developer_id>')
def dev_log_list(developer_id):  # put application's code here
    for_dev = db.dev_id_to_name(developer_id)
    dev_logs = db.select_dev_logs(developer_id)
    devs = db.select_all_devs()
    return render_template('log_list.html', all_logs=dev_logs, devs=devs, for_dev=for_dev)


@app.route('/delete_dev/<int:developer_id>')
def dev_delete(developer_id):
    db.delete_dev(developer_id)
    return redirect('/devs')


@app.route('/devs')
def dev_form():  # put application's code here
    devs = db.select_all_devs()
    return render_template('dev_form.html', devs=devs)


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


@app.route('/new', methods=['POST', 'GET'])
def log_form():  # put application's code here
    langs = db.list_langs()
    devs = db.select_all_devs()
    log = []
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
    return render_template('_log_form.html', devs=devs, langs=langs, log=log)


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


@app.route('/edit/<int:log_id>', methods=['POST', 'GET'])
def log_update(log_id):
    langs = db.list_langs()
    devs = db.select_all_devs()
    log = db.select_one_log(log_id)
    if request.method == 'POST':
        name = request.form.get('dev', type=str)
        work_date = request.form.get('work_date', type=str)
        lang = request.form.get('lang', type=str)
        duration = request.form.get('duration', type=int)
        rating = request.form.get('rating', type=int)
        note = request.form.get('note', type=str)
        result = db.update_log(log_id, name, work_date, lang, duration, rating, note)
        if result == 'Error':
            abort(400, 'Developer or log does not exist.')
    return render_template('_log_form.html', devs=devs, langs=langs, log=log)


if __name__ == '__main__':
    app.run()
