import click
from flask import current_app, g
from flask.cli import with_appcontext

import sqlite3


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


def insert_log(content, username):
    get_db().execute('insert into record (content, username) values (?,?)',
                     (content, username))
    get_db().commit()


def delete_note(id):
    get_db().execute('delete from record where id=?', (id,))
    get_db().commit()


def select_notes():
    cur = get_db().execute('select * from record')
    rows = cur.fetchall()
    print(rows)
    notes = []
    for row in rows:
        note = [row['content'], row['username'], row['id']]
        print(row['content'])
        notes.append(note)
    return notes
