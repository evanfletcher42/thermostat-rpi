from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
	user = { 'nickname': 'Evan'} #fake user
	posts = [ #fake array of posts
		{
			'author': { 'nickname': 'John'}, 
			'body': 'Beautiful day in Portland!'
		}, 
		{
			'author': { 'nickname': 'Susan' },
			'body': 'Test post please ignore'
		}
	]
	return render_template("index.html", title = 'Home', user=user, posts = posts)
