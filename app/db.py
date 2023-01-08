import click
from flask import current_app, g
from flask.cli import with_appcontext

import sqlite3
import re


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """
    Inicializuje databázi dle schema.sql
    """
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    Definujeme příkaz příkazové řádky
    """
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def select_all_logs():
    rows = query_db('select * from devlog dl join developer d on dl.developer_id = d.id')
    logs = []
    for row in rows:
        logs.append(SingleLog(row['id'], row['work_date'], row['lang'], row['duration'], row['rating'], row['note'],
                              row['name']))
    return logs


def select_all_devs():
    rows = query_db('select * from developer order by name')
    devs = []
    for row in rows:
        devs.append(row['name'])
    return devs


def insert_log(name, work_date, lang, duration, rating, note):
    print(name)
    cur = get_db().execute('select id from developer where name=? limit 1', (name,))
    row = cur.fetchone()
    cur.close()
    dev_id = row['id']
    g.db.execute('insert into devlog (work_date, lang, duration, rating, note, developer_id) values (?,?,?,?,?,?)',
                 (work_date, lang, duration, rating, note, dev_id))
    g.db.commit()



class SingleLog:
    def __init__(self, log_id, work_date, lang, duration, rating, note, developer_name):
        self.log_id = log_id
        self.work_date = work_date
        self.lang = lang
        self.duration = duration
        self.rating = rating
        self.note = note
        self.developer_name = developer_name

    def lang_css(self):
        lower_lang = self.lang.lower()
        return re.sub('[^a-zA-Z]', '_', lower_lang)
