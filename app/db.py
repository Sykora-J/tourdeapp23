from datetime import datetime
from time import strptime

import click
from flask import current_app, g
from flask.cli import with_appcontext

import sqlite3
import re
import bcrypt


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


def user_auth(mail_or_username, password):
    # authenticates the user. If not authenticated returns an error else returns username and if admin
    cur = get_db().execute('select username from developer where username=? limit 1', (mail_or_username,))
    username = cur.fetchone()
    cur.close()
    if username is None:
        cur = get_db().execute('select username from developer where mail=? limit 1', (mail_or_username,))
        username = cur.fetchone()
        cur.close()
    if username is None:
        return "User not found"
    username = str(username[0])
    cur = get_db().execute('select password from developer where username=? limit 1', (username,))
    db_password = cur.fetchone()[0]
    print(db_password)
    cur.close()
    if db_password == password:
        cur = get_db().execute('select bool_admin from developer where username=? limit 1', (username,))
        admin = bool(cur.fetchone()[0])
        cur.close()
        cur = get_db().execute('select id from developer where username=? limit 1', (username,))
        user_id = int(cur.fetchone()[0])
        cur.close()
        user = User(user_id, username, admin)
        return user
    return "Invalid password"


def select_dev_logs(developer_id):
    rows = query_db(
        'select * from devlog dl join developer d on dl.developer_id = d.id '
        'where developer_id=? order by work_date desc, dl.id desc', (developer_id,))
    dev_logs = []
    last_date = datetime.strptime('0001-01-01', "%Y-%m-%d")
    for row in rows:
        date = datetime.strptime(row['work_date'], "%Y-%m-%d")
        if last_date != date:
            one_date = SingleDate(date.strftime("%d.%m.%Y"))
            dev_logs.append(one_date)
            last_date = date
        one_date.add_log(row['id'], date.strftime("%d.%m.%Y"), row['lang'], row['duration'], row['rating'], row['note'])
    return dev_logs


def select_one_log(log_id):
    cur = get_db().execute('select * from devlog where id=? limit 1', (log_id,))
    row = cur.fetchone()
    cur.close()
    return row  # TODO ošetřit v app.py


# TODO insert_dev ERROR - same name
# TODO delete_dev ERROR - already deleted
# TODO delete_log half done
# TODO delete_log ERROR - already deleted
# TODO update_log half done
# TODO update_dev

def select_all_users():
    rows = query_db('select * from developer order by username')
    devs = []
    for row in rows:
        devs.append(CompleteUser(row['id'], row['fname'], row['lname'],
                                 row['username'], row['mail'], row['password'], bool(row['bool_admin'])))
    return devs  # devs is a list containing CompleteUsers


def insert_log(dev_id, work_date, lang, duration, rating, note):
    if dev_id is None:
        return 'Error'
    get_db().execute('insert into devlog (work_date, lang, duration, rating, note, developer_id) values (?,?,?,?,?,?)',
                     (work_date, lang, duration, rating, note, dev_id))
    get_db().commit()
    return 'OK'


def delete_log(log_id, user_id):
    cur = get_db().execute('select developer_id from devlog where id=? limit 1', (log_id,))
    row = cur.fetchone()
    cur.close()
    if row is None:
        return "Error - Log doesn't exist"
    if row['developer_id'] == user_id:
        get_db().execute('delete from devlog where id=?', (log_id,))
        get_db().commit()
        return "OK"
    return "Error - no permission"


def update_log(log_id, dev_id, work_date, lang, duration, rating, note):
    cur = get_db().execute('select developer_id from devlog where id=? limit 1', (log_id,))
    row = cur.fetchone()
    cur.close()
    if row is None:
        return "Error - Log doesn't exist"
    if row['developer_id'] == dev_id:
        try:
            get_db().execute(
                'update devlog set work_date=?, lang=?, duration=?, rating=?, note=?, developer_id=?  where id=?',
                (work_date, lang, duration, rating, note, dev_id, log_id))
        except sqlite3.Error as e:
            return 'Error - Database error'
        get_db().commit()
        return 'OK'
    return "Error - no permission"


def insert_dev(fname, lname, username, mail, password, bool_admin):
    try:
        get_db().execute('insert into developer (fname, lname, username, mail, password, bool_admin) values (?,?,?,?,?,?)',
                         (fname, lname, username, mail, password, bool_admin))
    except sqlite3.Error as e:
        return 'Error - username or mail already exists'
    get_db().commit()
    return 'OK'


def delete_dev(dev_id):
    get_db().execute('delete from developer where id=?', (dev_id,))
    get_db().commit()
    get_db().execute('delete from devlog where developer_id=?', (dev_id,))
    get_db().commit()


def update_dev(dev_id, new_name):
    try:
        get_db().execute('update developer set username=?  where id=?', (new_name, dev_id))
    except sqlite3.Error as e:
        return 'Error'
    get_db().commit()
    return 'OK'


def list_langs():
    langs = ['Python', 'Java', 'C++', 'Pascal', 'HTML:o)', 'Javascript']
    return langs


def dev_id_to_name(dev_id):
    cur = get_db().execute('select username from developer where id=? limit 1', (dev_id,))
    row = cur.fetchone()
    cur.close()
    if row is None:
        return None
    name = row['username']
    return name


def dev_name_to_id(name):
    cur = get_db().execute('select id from developer where username=? limit 1', (name,))
    row = cur.fetchone()
    cur.close()
    if row is None:
        return None
    dev_id = row['id']
    return dev_id


class User:
    def __init__(self, user_id, username, admin):
        self.user_id = user_id
        self.username = username
        self.admin = admin


class CompleteUser:
    def __init__(self, user_id, fname, lname, username, mail, password, bool_admin):
        self.user_id = user_id
        self.fname = fname
        self.lname = lname
        self.username = username
        self.mail = mail
        self.password = password
        self.bool_admin = bool_admin


class SingleLog:
    def __init__(self, log_id, work_date, lang, duration, rating, note):
        self.log_id = log_id
        self.work_date = work_date
        self.lang = lang
        self.duration = duration
        self.rating = rating
        self.note = note

    def lang_css(self):
        lower_lang = self.lang.lower()
        return re.sub('[^a-zA-Z]', '_', lower_lang)


class SingleDate:
    def __init__(self, work_date):
        self.work_date = work_date
        self.logs = []

    def add_log(self, log_id, work_date, lang, duration, rating, note):
        self.logs.append(SingleLog(log_id, work_date, lang, duration, rating, note))
        return self.logs
