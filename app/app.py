import os

from flask import Flask, render_template, request, redirect
from . import db
import requests

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
def sticky_notes_board():
    return redirect('/notes')


@app.route('/notes')
def notes():
    notes = db.select_notes()
    print(notes)
    return render_template('notes.html', notes=notes)


@app.route('/new', methods=['POST', 'GET'])
def new():
    if request.method == 'POST':
        content = request.form.get('content', type=str)
        username = request.form.get('username', type=str)
        db.insert_log(content, username)
    return redirect('/notes')


@app.route('/edit/<int:id>', methods=['POST', 'GET'])
def edit(id):
    if request.method == 'POST':
        content = request.form.get('content', type=str)
        username = request.form.get('username', type=str)
        db.edit_note(id, content, username)
    return redirect('/notes')


@app.route('/delete/<int:id>')
def delete(id):
    db.delete_note(id)
    return redirect('/notes')




@app.route('/server')
def server_stats():
    sysinfo = requests.get("https://tda.knapa.cz/sysinfo/", headers={'x-access-token': 'e3945df7c4b039479b1bdc92c6126ee1'})
    cpu = str(100*sysinfo.json()['cpu_load'])+' %'
    ram = str(sysinfo.json()['ram_usage'])+' %'
    disk = str(sysinfo.json()['disk_usage'])+' %'
    boot = sysinfo.json()['boot_time']
    platform = sysinfo.json()['platform']
    last_commit = requests.get("https://tda.knapa.cz/commit/latest/1", headers={'x-access-token': 'e3945df7c4b039479b1bdc92c6126ee1'})
    ldate = last_commit.json()[0]['date']
    ladded = last_commit.json()[0]['lines_added']
    lremoved = last_commit.json()[0]['lines_removed']
    ldesc = last_commit.json()[0]['description']
    last_commit_userid = last_commit.json()[0]['creator_id']
    last_user = requests.get("https://tda.knapa.cz/user/"+str(last_commit_userid), headers={'x-access-token': 'e3945df7c4b039479b1bdc92c6126ee1'})
    last_name = last_user.json()['name']
    last_surname = last_user.json()['surname']
    last_nick = last_user.json()['nick']
    return render_template('server.html',
    cpu=cpu, ram=ram, disk=disk, boot=boot, platform=platform, last_name=last_name, last_surname=last_surname,
    last_nick=last_nick, ldate=ldate, ladded=ladded, lremoved=lremoved, ldesc=ldesc)


if __name__ == '__main__':
    app.run()
