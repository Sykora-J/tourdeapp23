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
def log_list():  # put application's code here
    for_dev = request.args.get('dev', 'All')
    logs = db.select_all_logs()
    devs = db.select_all_devs()
    return render_template('log_list.html', logs=logs, devs=devs, for_dev=for_dev)


@app.route('/devs')  # TODO take out dev_id
def dev_form():  # put application's code here
    devs = db.select_all_devs()  # TODO log for only one dev
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
