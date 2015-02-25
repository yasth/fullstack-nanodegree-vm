"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from catalog import app,db,models

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/catalog.json')
def recentJsonify():
    """Return Json of recent files"""
    return flask.jsonify(**f)

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/login')
def login():
    """Renders the contact page."""
    return render_template(
        'login.html',
        title='login',
        year=datetime.now().year,
        message=''
    )

@app.route('/category/<int:id>')
def category(id):
    """Renders the about page."""
    cat = models.Category.get(id)
    return render_template(
        'category.html',
        title=cat.Name,
        items = cat.Items
        
    )
