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
def hello_world():  # put application's code here
    return "Hello Tour de App!"


@app.route('/list')
def log_list():  # put application's code here
    for_dev = request.args.get('dev', 'all')
    logs = db.select_all_logs() # TODO log for only one dev
    devs = db.select_all_devs()
    return render_template('log_list.html', logs=logs, devs=devs, for_dev=for_dev)


if __name__ == '__main__':
    app.run()
