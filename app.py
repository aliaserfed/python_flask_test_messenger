import sqlite3

from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(SECRET_KEY='dev')


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)')
            usernames = list()
            for account in cur.execute('SELECT * FROM users'):
                if request.form['username'] == account[0] and request.form['password'] == account[1]:
                    session['username'] = request.form['username']
                    session['password'] = request.form['password']
                    return redirect(url_for('user', username=request.form['username']))
                usernames.append(account[0])
            if request.form['username'] not in usernames:
                cur.execute('INSERT INTO users VALUES(?, ?)', [request.form['username'], request.form['password']])
                session['username'] = request.form['username']
                session['password'] = request.form['password']
                return redirect(url_for('user', username=request.form['username']))
    if 'username' in session:
        return redirect(url_for('user', username=session['username']))
    return render_template('index.html')


@app.route('/<path:username>', methods=['POST', 'GET'])
def user(username):
    if request.method == 'POST':
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('INSERT INTO chat VALUES(?, ?)', [username, request.form['message']])
    if 'username' in session and username == session['username']:
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS chat(user TEXT NOT NULL, message TEXT)')
            messages = ''
            for i, message in enumerate(cur.execute('SELECT * FROM chat').fetchall()):
                if i != 0:
                    messages += '\n'
                messages += f'{message[0]}: {message[1]}'
            return render_template('messages.html', messages=messages, username=username)
    return redirect(url_for('login'))


@app.route('/exit', methods=['POST'])
def exit_quit():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
