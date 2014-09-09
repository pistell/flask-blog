from flask import Flask, render_template, request, session, flash, redirect, url_for, g
from functools import wraps
import sqlite3

#config
DATABASE = 'blog.db'
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET_KEY = 'hard_to_guess'

app = Flask(__name__)


#pulls in app config by looking for uppercase vars
app.config.from_object(__name__)

#func used to connect to db 
def connect_db():
	return sqlite3.connect(app.config['DATABASE'])


def login_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return test(*args, **kwargs)
		else:
			flash('You need to be logged in first')
			return redirect(url_for('login'))
	return wrap


@app.route('/', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid Credentials. Please Try Again'
		else:
			session['logged_in'] = True
			return redirect(url_for('main'))
	return render_template('login.html', error=error)



@app.route('/main')
@login_required
def main():
	g.db = connect_db()
	cur = g.db.execute('SELECT * FROM posts')
	posts = [dict(title=row[0], post=row[1]) for row in cur.fetchall()]
	g.db.close()
	return render_template('main.html', posts=posts)

@app.route('/add', methods=['POST'])
@login_required
def add():
	title = request.form['title']
	post = request.form['post']
	if not title or not post:
		flash('All fields required. Please try again')
		return redirect(url_for('main'))
	else:
		g.db = connect_db()
		g.db.execute('INSERT INTO posts (title, post) VALUES (?, ?)', [request.form['title'], request.form['post']])
		g.db.commit()
		g.db.close()
		flash('New entry was successfully posted!')
		return redirect(url_for('main'))



@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You have been logged out')
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.run(debug=True)