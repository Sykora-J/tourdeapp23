import os
from datetime import datetime

import werkzeug
from flask import Flask, abort, jsonify, make_response, flash, get_flashed_messages, url_for, send_from_directory
from flask import render_template
from flask import redirect
from flask import request
from flask import session
import csv
import io
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


@app.route('/')
def all_log_list():  # put application's code here
    if 'user_id' in session:
        dev_logs = db.select_dev_logs(session["user_id"])
        admin = session["admin"]
        log = []
        langs = db.list_langs()
        username = session['username']
        showtoast = get_flashed_messages()
        if len(showtoast) == 0:
            showtoast = None
        return render_template('log_list.html', dev_logs=dev_logs, log=log, langs=langs,
                               admin=admin, username=username, showtoast=showtoast)
    return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    error_message = None
    user_or_mail = ''
    if request.method == 'POST':
        user_or_mail = request.form.get('user_or_mail', type=str)
        password = request.form.get('password', type=str)
        user = db.user_auth(user_or_mail, password)
        if type(user) is db.User:
            session["user_id"] = user.user_id
            session["username"] = user.username
            session["admin"] = user.admin
            return redirect('/')
        else:
            error_message = 'Wrong login credentials'
    username = ""
    return render_template('login.html', username=username, error_message=error_message)


@app.route('/devs')
def dev_form():  # put application's code here
    if not session['admin']:
        return redirect('/')
    devs = db.select_all_users()
    log = []
    langs = db.list_langs()
    user_id = session['user_id']
    admin = session['admin']
    username = session['username']
    showtoast = get_flashed_messages()
    if len(showtoast) == 0:
        showtoast = None
    return render_template('dev_list.html', devs=devs, log=log, langs=langs, user_id=user_id,
                           admin=admin, username=username, showtoast=showtoast)


@app.route('/edit_log/<int:log_id>')
def log_update_form(log_id):
    langs = db.list_langs()
    log = db.select_one_log(log_id)
    username = session['username']
    return render_template('edit_log_form.html', langs=langs, log=log, username=username)


@app.route('/edit_user/<int:dev_id>')
def dev_update_form(dev_id):
    if not session['admin']:
        return redirect('/')
    langs = db.list_langs()
    user = db.select_one_dev(dev_id)
    admin = session['admin']
    if type(user) is str:
        flash(user)
        return redirect('/')
    user_id = session["user_id"]
    username = session['username']
    return render_template('edit_user_form.html', langs=langs, user=user, admin=admin, user_id=user_id, username=username)


@app.route('/about')
def about():
    username = session['username']
    langs = db.list_langs()
    user_id = session["user_id"]
    admin = session['admin']
    return render_template('about.html', username=username, admin=admin, user_id=user_id, langs=langs)


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('admin', None)
    return redirect('/')


@app.route('/delete_dev/<int:developer_id>')
def dev_delete(developer_id):
    if session['admin']:
        if session['user_id'] != developer_id:
            response = db.delete_dev(developer_id)
        else:
            flash("Error - you cannot delete yourself")
            response = ""
        if "Error" in response:
            flash(response)
        return redirect('/devs')
    flash('Error - Invalid permission')
    return redirect('/')


@app.route('/new_user', methods=['POST', 'GET'])
def dev_insert():  # put application's code here
    if session['admin']:
        if request.method == 'POST':
            fname = request.form.get('fname', type=str).strip()
            lname = request.form.get('lname', type=str).strip()
            username = request.form.get('username', type=str).strip()
            mail = request.form.get('mail', type=str).strip()
            password = request.form.get('password', type=str)
            if "@" in username:
                flash("Error - username can't contain @")
                return redirect('/devs')
            if request.form.get('admin'):
                bool_admin = 1
            else:
                bool_admin = 0
            if all([fname != "", lname != "", username != "", mail != "", password != "", ]):
                result = db.insert_dev(fname, lname, username, mail, password, bool_admin)
                if "Error" in result:
                    flash(result)
            else:
                flash("Error - something is missing")
        return redirect('/devs')
    return redirect('/')


@app.route('/dev_edit/<int:dev_id>', methods=['POST', 'GET'])
def dev_edit(dev_id):  # put application's code here
    if session['admin']:
        if request.method == 'POST':
            fname = request.form.get('fname', type=str).strip()
            lname = request.form.get('lname', type=str).strip()
            username = request.form.get('username', type=str).strip()
            mail = request.form.get('mail', type=str).strip()
            password = request.form.get('password', type=str)
            if "@" in username:
                flash("Error - username can't contain @")
                return redirect('/devs')
            if request.form.get('admin'):
                bool_admin = 1
            else:
                bool_admin = 0
            if dev_id == session['user_id']:
                bool_admin = 1
            if all([fname != "", lname != "", username != "", mail != "", password != "", ]):
                result = db.update_dev(dev_id, fname, lname, username, mail, password, bool_admin)
                if "Error" in result:
                    flash(result)
                elif dev_id == session['user_id']:
                    session['username'] = username
            else:
                flash("Error - something is missing")
        return redirect('/devs')
    return redirect('/')


@app.route('/new_log', methods=['POST', 'GET'])
def log_form():  # put application's code here
    if request.method == 'POST':
        dev_id = session["user_id"]
        work_date = request.form.get('work_date', type=str)
        lang = request.form.get('lang', type=str)
        duration = request.form.get('duration', type=int)
        rating = request.form.get('rating', type=int)
        note = request.form.get('note', type=str)
        result = db.insert_log(dev_id, work_date, lang, duration, rating, note)
        if result == 'Error':
            flash('Developer does not exist.')
    return redirect('/')


@app.route('/delete_log/<int:log_id>')
def log_delete(log_id):
    result = db.delete_log(log_id, session['user_id'])
    if "Error" in result:
        flash(result)
    return redirect('/')


@app.route('/edit/<int:log_id>', methods=['POST', 'GET'])
def log_update(log_id):
    if request.method == 'POST':
        work_date = request.form.get('work_date', type=str)
        lang = request.form.get('lang', type=str)
        duration = request.form.get('duration', type=int)
        rating = request.form.get('rating', type=int)
        note = request.form.get('note', type=str)
        result = db.update_log(log_id, session['user_id'], work_date, lang, duration, rating, note)
        if "Error" in result:
            flash(result)
    return redirect('/')


def is_integer():
    pass


# update bitch
@app.route('/upload_logs', methods=['GET', 'POST'])
def upload_logs():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash("Error - no file")
            return redirect('/')
        file = request.files['file']
        # if user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            flash("Error - no file name")
            return redirect('/')
        if file and db.allowed_file(file.filename):
            try:
                # read the CSV file
                stream = io.StringIO(file.stream.read().decode("cp1250"), newline=None)
                reader = csv.reader(stream)
                # skip the header row
                if len(next(reader)) != 5:
                    flash("Error - invalid file structure")
                    return redirect('/')
                # iterate over each row and insert the log
                failed_rows = 0
                for row in reader:
                    try:
                        date, duration, lang, rating, note = row
                        date = datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
                        duration = int(duration)
                        rating = int(rating)
                        if all([1 <= duration <= 1440, 1 <= len(lang) <= 20, 1 <= rating <= 5, len(note) <= 256]):
                            db.insert_log(session['user_id'], date, lang, duration, rating, note)
                        else:
                            failed_rows = failed_rows + 1
                    except Exception as e:
                        failed_rows = failed_rows + 1
                if failed_rows != 0:
                    flash("Error - skipped rows: " + str(failed_rows))
            except Exception:
                flash("Error - something went wrong")
        else:
            flash('Error - invalid file type')
    return redirect('/')


@app.route('/download_logs')
def download_logs():
    user_id = session['user_id']
    username = session['username']
    # fetch the logs for the given user_id from the database
    logs = db.select_dev_logs(user_id)

    # create a buffer object to write the CSV data
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    # write the header row
    writer.writerow(['id', 'date', 'time_spent', 'programming_language', 'rating', 'description'])

    # write each log as a row in the CSV
    for date in logs:
        for log in date.logs:
            writer.writerow([log.log_id, log.work_date, log.duration, log.lang, log.rating, log.note])

    # create a response object with a CSV attachment
    response = make_response(buffer.getvalue())
    date = datetime.now().strftime('%Y-%m-%d')
    response.headers['Content-Disposition'] = f'attachment; filename={username}-{date}.csv'
    response.headers['Content-type'] = 'text/csv'

    # return the response
    return response


@app.route('/users/<int:user_id>/records/<int:record_id>', methods=['DELETE'])
def delete_user_record(user_id, record_id):
    # Replace with your own implementation to delete the record based on user_id and record_id
    result = db.delete_log(record_id, user_id)
    if result == "Error - Log doesn't exist":
        return jsonify({"message": "Record not found"}), 404
    elif result == "Error - no permission":
        return jsonify({"message": "User does not have permission to delete this record"}), 403
    else:
        return jsonify({"message": "Record deleted successfully"}), 200


@app.route('/users/<int:user_id>/records/<int:record_id>', methods=['GET'])
def get_user_record(user_id, record_id):
    # Replace with your own implementation to fetch the record based on user_id and record_id
    log = db.select_one_log(record_id)
    if log is None:
        return 404
    if log["developer_id"] == user_id:
        record = {
            "id": log["id"],
            "date": log["work_date"],
            "time_spent": log["duration"],
            "programming_language": log["lang"],
            "rating": log["rating"],
            "description": log["note"]
        }
        return jsonify(record), 200


@app.route('/users/<int:user_id>/records/<int:record_id>', methods=['PUT'])
def update_user_record(user_id, record_id):
    log = db.select_one_log(record_id)
    if log is None:
        return 'Error - Log does not exist', 404
    if log['developer_id'] != user_id:
        return 'Error - no permission', 403
    data = request.get_json()
    try:
        work_date = data['date']
        lang = data['programming_language']
        duration = data['time_spent']
        rating = data['rating']
        note = data['description']
    except KeyError:
        return 'Error - Invalid input data', 400
    result = db.update_log(record_id, user_id, work_date, lang, duration, rating, note)
    if result == 'OK':
        return jsonify(data), 200
    elif result == 'Error - Log does not exist':
        return result, 404
    elif result == 'Error - no permission':
        return result, 403
    else:
        return result, 500


@app.route('/users/<int:user_id>/records', methods=['GET'])
def get_user_records(user_id):
    logs = db.select_dev_logs(user_id)
    if len(logs) == 0:
        return "Error - User doesn't exist", 404
    response = []
    for log in logs:
        for single_log in log.logs:
            response.append({
                "id": single_log.log_id,
                "date": single_log.work_date,
                "time_spent": single_log.duration,
                "programming_language": single_log.lang,
                "rating": single_log.rating,
                "description": single_log.note
            })
    return jsonify(response)


@app.route('/users/<int:user_id>/records', methods=['POST'])
def add_record(user_id):
    data = request.json
    date = data.get('date')
    time_spent = data.get('time_spent')
    programming_language = data.get('programming_language')
    rating = data.get('rating')
    description = data.get('description')
    result = db.insert_log(user_id, date, programming_language, time_spent, rating, description)
    if result == 'OK':
        log_id = db.last_insert_id()
        record = {
            'id': log_id,
            'date': date,
            'time_spent': time_spent,
            'programming_language': programming_language,
            'rating': rating,
            'description': description
        }
        return jsonify(record), 201
    else:
        return 'Error', 400


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.errorhandler(werkzeug.exceptions.HTTPException)
def error_handler(exception):
    try:
        username = session['username']
    except KeyError:
        username = ""
    return render_template('error_page.html', username=username)


if __name__ == '__main__':
    app.run()
