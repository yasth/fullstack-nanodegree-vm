from flask import Flask, render_template, request, redirect,jsonify, url_for
from functools import wraps
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item



app = Flask(__name__)


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()



def login_required(f):
    """Requires login function decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

#Fake Categories
#category = {'name': 'The CRUDdy Crab', 'id': '1'}

#restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


#Fake Menu Items
#items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
#item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}




#@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
#def restaurantMenuJSON(restaurant_id):
#	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
#	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
#	return jsonify(MenuItems=[i.serialize for i in items])



#@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
#def menuItemJSON(restaurant_id, menu_id):
#	Menu_Item = session.query(MenuItem).filter_by(id = menu_id).one()
#	return jsonify(Menu_Item = Menu_Item.serialize)

#@app.route('/restaurant/JSON')
#def restaurantsJSON():
#	restaurants = session.query(Restaurant).all()
#	return jsonify(restaurants= [r.serialize for r in restaurants])

@oauth.clientgetter
def load_client(client_id):
    return session.query(Client).filter_by(client_id=client_id).first()

@oauth.grantgetter
def load_grant(client_id, code):
    return session.query(Grant).filter_by(client_id=client_id, code=code).first()

@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    # decide the expires time yourself
    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=get_current_user(),
        expires=expires
    )
    session.add(grant)
    session.commit()
    return grant

@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return session.query(Token).filter_by(access_token=access_token).first()
    elif refresh_token:
        return session.query(Token).filter_by(refresh_token=refresh_token).first()

from datetime import datetime, timedelta

@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    toks = session.query(Token).filter_by(client_id=request.client.client_id,
                                 user_id=request.user.id)
    # make sure that every client has only one token connected to a user
    for t in toks:
        session.delete(t)

    expires_in = token.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    tok = Token(
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        _scopes=token['scope'],
        expires=expires,
        client_id=request.client.client_id,
        user_id=request.user.id,
    )
    session.add(tok)
    session.commit()
    return tok

@app.route('/oauth/authorize', methods=['GET', 'POST'])
@require_login
@oauth.authorize_handler
def authorize(*args, **kwargs):
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = session.query(Client).filter_by(client_id=client_id).first()
        kwargs['client'] = client
        return render_template('oauthorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'

@app.route('/')
@app.route('/catalog/')
@app.route('/home')
def home():
    """Show all categories and most recent items"""
    categories = session.query(Category).all()
    items = session.query(Item).order_by(desc(Item.pub_date)).limit(20).all() #get top 20 most recent items
    return render_template('index.html', categories = categories, items=items)
	
@app.route('/category/<id>')
def getCategory(id=-1):
    categories = session.query(Category).all()
    thisCat = session.query(Category).get(id)
    return render_template('getCategory.html', categories = categories, thisCat=thisCat)
	

@app.route('/item/<title>')
def getItem(title):
    categories = session.query(Category).all()
    thisItem = session.query(Item).filter_by(title=title).one()
    return render_template('getItem.html', categories = categories, thisItem=thisItem)
	



	

##Create a new restaurant
#@app.route('/restaurant/new/', methods=['GET','POST'])
#def newRestaurant():
#	if request.method == 'POST':
#		newRestaurant = Restaurant(name = request.form['name'])
#		session.add(newRestaurant)
#		session.commit()
#		return redirect(url_for('showRestaurants'))
#	else:
#		return render_template('newRestaurant.html')
#	#return "This page will be for making a new restaurant"

##Edit a restaurant
#@app.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
#def editRestaurant(restaurant_id):
#	editedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
#	if request.method == 'POST':
#		if request.form['name']:
#			editedRestaurant.name = request.form['name']
#			return redirect(url_for('showRestaurants'))
#	else:
#		return render_template('editRestaurant.html', restaurant = editedRestaurant)

#	#return 'This page will be for editing restaurant %s' % restaurant_id

##Delete a restaurant
#@app.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET','POST'])
#def deleteRestaurant(restaurant_id):
#	restaurantToDelete = session.query(Restaurant).filter_by(id = restaurant_id).one()
#	if request.method == 'POST':
#		session.delete(restaurantToDelete)
#		session.commit()
#		return redirect(url_for('showRestaurants', restaurant_id = restaurant_id))
#	else:
#		return render_template('deleteRestaurant.html',restaurant = restaurantToDelete)
#	#return 'This page will be for deleting restaurant %s' % restaurant_id


##Show a restaurant menu
#@app.route('/restaurant/<int:restaurant_id>/')
#@app.route('/restaurant/<int:restaurant_id>/menu/')
#def showMenu(restaurant_id):
#	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
#	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
#	return render_template('menu.html', items = items, restaurant = restaurant)
#	 #return 'This page is the menu for restaurant %s' % restaurant_id

##Create a new menu item
#@app.route('/restaurant/<int:restaurant_id>/menu/new/',methods=['GET','POST'])
#def newMenuItem(restaurant_id):
#	if request.method == 'POST':
#		newItem = MenuItem(name = request.form['name'], description = request.form['description'], price = request.form['price'], course = request.form['course'], restaurant_id = restaurant_id)
#		session.add(newItem)
#		session.commit()
		
#		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
#	else:
#		return render_template('newmenuitem.html', restaurant_id = restaurant_id)

#	return render_template('newMenuItem.html', restaurant = restaurant)
#	#return 'This page is for making a new menu item for restaurant %s' %restaurant_id

##Edit a menu item
#@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET','POST'])
#def editMenuItem(restaurant_id, menu_id):
#	editedItem = session.query(MenuItem).filter_by(id = menu_id).one()
#	if request.method == 'POST':
#		if request.form['name']:
#			editedItem.name = request.form['name']
#		if request.form['description']:
#			editedItem.description = request.form['name']
#		if request.form['price']:
#			editedItem.price = request.form['price']
#		if request.form['course']:
#			editedItem.course = request.form['course']
#		session.add(editedItem)
#		session.commit() 
#		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
#	else:
		
#		return render_template('editmenuitem.html', restaurant_id = restaurant_id, menu_id = menu_id, item = editedItem)

	
#	#return 'This page is for editing menu item %s' % menu_id

##Delete a menu item
#@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET','POST'])
#def deleteMenuItem(restaurant_id,menu_id):
#	itemToDelete = session.query(MenuItem).filter_by(id = menu_id).one() 
#	if request.method == 'POST':
#		session.delete(itemToDelete)
#		session.commit()
#		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
#	else:
#		return render_template('deleteMenuItem.html', item = itemToDelete)
#	#return "This page is for deleting menu item %s" % menu_id
if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
