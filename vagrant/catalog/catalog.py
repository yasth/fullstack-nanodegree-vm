from flask import Flask, render_template, request, redirect,jsonify, url_for,flash, session
from functools import wraps
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item
from flask_oauthlib.client import OAuth
from werkzeug.contrib.atom import AtomFeed


app = Flask(__name__)


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
dbSession = DBSession()


#
# OAuth 
#
def login_required(f):
    """Requires login function decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'twitter_user' not in session :
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

oauth = OAuth()
twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key='ReplaceMeWithConsumerKey', #TODO: This needs to be replaced with your own data
    consumer_secret='ReplaceMeWithConsumerSecret') #TODO: as does this



@twitter.tokengetter
def get_twitter_token(token=None):
    """gets the token for twitter"""
    return session.get('twitter_token')

@app.route('/login')
def login():
    """routes to twitter page or setup"""
    if twitter.consumer_key=="ReplaceMeWithConsumerKey":
        return  render_template('twitterSetup.html')
    return twitter.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))

@app.route('/oauth-authorized')
def oauth_authorized():
    """ call back function for twitter oauth """
    next_url = request.args.get('next') or url_for('index')
    resp = twitter.authorized_response()
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(url_for('home'))

    session['twitter_token'] = (resp['oauth_token'],
        resp['oauth_token_secret'])
    session['twitter_user'] = resp['screen_name']

    flash('You were signed in as %s' % resp['screen_name'])
    return redirect(next_url)

@app.route('/logout')
def logout():
    """ logs out the current user (will have to reauth) """
    session.pop('twitter_user',None)
    return redirect(url_for("home"))

# JSON endpoints
@app.route('/category/JSON')
def getCategoriesJSON():
    """returns list of all categories"""
    categories = dbSession.query(Category).all()
    return jsonify(categories= [c.serialize() for c in categories])

@app.route('/category/<categoryID>/JSON')
def getCategoryJSON(categoryID):
    """returns category information and items in category information"""
    category = dbSession.query(Category).get(categoryID)
    return jsonify(category = category.serialize(), items=[i.serialize() for i in category.Items])

@app.route('/item/JSON')
def getItemsJSON():
    """returns all items in json"""
    items = dbSession.query(Item).all()
    return jsonify(categories= [i.serialize() for i in items])


#Syndication
@app.route('/atom')
def atomFeed():
    """ATOM feed for syndication of most recently updated items"""
    items = dbSession.query(Item).order_by(desc(Item.pub_date)).limit(20).all() #get top 20 most recent items
    feed = AtomFeed('Recent Articles',
                    feed_url=request.url, url=request.url_root)
    for item in items:
        feed.add(item.title,unicode(item.body),content_type='html',published=item.pub_date,updated=item.pub_date, id=item.id)
    return feed.get_response()

#
# HTML endpoints
#


@app.route('/')
@app.route('/catalog/')
@app.route('/home')
def home():
    """Show all categories and most recent items"""
    categories = dbSession.query(Category).all()
    items = dbSession.query(Item).order_by(desc(Item.pub_date)).limit(20).all() #get top 20 most recent items
    return render_template('index.html', categories = categories, items=items)

@app.route('/category/<id>')
def getCategory(id=-1):
    """Gets a single category and items in it"""
    categories = dbSession.query(Category).all()
    thisCat = dbSession.query(Category).get(id)
    return render_template('getCategory.html', categories = categories, thisCat=thisCat)
    #return "this page will be for getting a category"

@app.route('/category/<categoryID>/edit', methods=['get','post'])
@login_required
def editCategory(categoryID):
    """edits the name of a category (req login)"""
    category = dbSession.query(Category).get(categoryID)
    if request.method.lower() == 'post':
        if request.form['name']:
            category.name = request.form['name']
        dbSession.add(category)
        dbSession.commit()
        return redirect(url_for('home'))
    else:
        return render_template('editCategory.html',category = category)
    #return "this page will be for adding a category"

@app.route('/category/new/', methods=['get','post'])
@login_required
def addCategory():
    """Adds a category  (req login)"""
    if request.method.lower() == 'post':
		newCategory = Category(name = request.form['name'])
		dbSession.add(newCategory)
		dbSession.commit()
		return redirect(url_for('home'))
    else:
		return render_template('addCategory.html')
	#return "this page will be for adding a category"



@app.route('/category/<categoryID>/delete', methods=['get','post'])
@login_required
def deleteCategory(categoryID):
    """ Deletes a category and all items in it (req login)"""
    category = dbSession.query(Category).get(categoryID)
    if request.method.lower() == 'post':
         for item in category.Items:
             dbSession.delete(item)
         dbSession.delete(category)
         dbSession.commit()
         return redirect(url_for('home'))
    else:
        return render_template('deleteCategory.html',thisCategory=category)
        #return "this page will be for deleting a category"



@app.route('/item/<title>)')
def getItem(title):
    """ gets a single items information """
    categories = dbSession.query(Category).all()
    thisItem = dbSession.query(Item).filter_by(title=title).one()
    return render_template('getItem.html', categories = categories, thisItem=thisItem)
    #return "this page will be for getting an item"


@app.route('/item/new/<categoryID>', methods=['get','post'])
@login_required
def addItem(categoryID):
    """ adds an item to a category  (req login)"""
    if request.method.lower() == 'post':
        category = dbSession.query(Category).get(categoryID)
        newItem = Item(request.form['title'],request.form['body'],request.form['url'],category)
        dbSession.add(newItem)
        dbSession.commit()
        return redirect(url_for('getCategory',id = categoryID))
    else:
        return render_template('addItem.html')
        #return "this page will be for making a new item"


@app.route('/item/<itemID>/edit', methods=['get','post'])
@login_required
def editItem(itemID):
    """ edits the details of an item  (req login)"""
    item = dbSession.query(Item).get(itemID)
    if request.method.lower() == 'post':
         if request.form['title']:
             item.title =  request.form['title']
         if request.form['body']:
             item.body =  request.form['body']
         if request.form['url']:
             item.url =  request.form['url']
         if request.form['categoryID']:
             category = dbSession.query(Category).get(int(request.form['categoryID']))
             item.category =  category
         dbSession.add(item)
         dbSession.commit()
         return redirect(url_for('getItem',title = item.title))
    else:
        categories = dbSession.query(Category).all()
        return render_template('editItem.html',item=item, categories=categories)
        #return "this page will be for editting an item"

        

@app.route('/item/<itemID>/delete', methods=['get','post'])
@login_required
def deleteItem(itemID):
    """ deletes an item  (req login)"""
    item = dbSession.query(Item).get(itemID)
    if request.method.lower() == 'post':
         dbSession.delete(item)
         dbSession.commit()
         return redirect(url_for('home'))
    else:
        return render_template('deleteItem.html',thisItem=item)
        #return "this page will be for deleteing an item"



	

if __name__ == '__main__':
    app.secret_key = 'hunter2' 
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
