import os

from flask import Flask
from flask import render_template
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
    for row in db.query_db('select * from devlog dl join developer d on dl.developer_id = d.id'):
        print(row['work_date'], ' Language: ', row['lang'])
    rows = db.query_db('select * from devlog dl join developer d on dl.developer_id = d.id')
    return render_template('log_list.html', rows=rows)


if __name__ == '__main__':
    app.run()
