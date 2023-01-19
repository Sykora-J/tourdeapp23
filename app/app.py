import os

from flask import Flask
from flask import render_template
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


@app.route('/dev/<developer_id>')
def dev_log_list(developer_id):  # put application's code here
    for_dev = db.dev_id_to_name(developer_id)
    dev_logs = db.select_dev_logs(developer_id)
    devs = db.select_all_devs()
    return render_template('log_list.html', all_logs=dev_logs, devs=devs, for_dev=for_dev)


# TODO delete_dev
# TODO delete_log
# TODO update_log


@app.route('/devs')
def dev_form():  # put application's code here
    devs = db.select_all_devs()
    all_logs = db.select_all_logs()
    print(all_logs[2].logs)
    return render_template('dev_form.html', devs=devs)


@app.route('/new', methods=['POST', 'GET'])
def log_form():  # put application's code here
    langs = ['Python', 'Java', 'C++']  # TODO make it better
    devs = db.select_all_devs()
    if request.method == 'POST':
        name = request.form.get('dev', type=str)
        work_date = request.form.get('work_date', type=str)
        lang = request.form.get('lang', type=str)
        duration = request.form.get('duration', type=int)
        rating = request.form.get('rating', type=int)
        note = request.form.get('note', type=str)
        db.insert_log(name, work_date, lang, duration, rating, note)
    return render_template('log_form.html', devs=devs, langs=langs)


if __name__ == '__main__':
    app.run()
