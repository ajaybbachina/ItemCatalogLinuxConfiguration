from flask_login import (LoginManager,
                         login_required,
                         current_user,
                         login_user,
                         logout_user)
import requests
from functools import wraps
from flask import make_response
import json
import httplib2
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
import string
import random
from flask import session as login_session
from itemCatalogDataSetup import Base, Category, CategoryItem, User
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, asc
from oauthlib.oauth2 import WebApplicationClient
from flask import (Flask,
                   g,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for,
                   flash)
from itemCatalogDataSetup import engine

# IMPORTS FOR THIS STEP


app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog App"

GOOGLE_CLIENT_ID = CLIENT_ID
GOOGLE_CLIENT_SECRET = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_secret']
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
                     for x in range(32))

login_manager = LoginManager()
login_manager.init_app(app)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Connect to Database and create database session
Base.metadata.create_all(engine)
engine1 = create_engine('sqlite:///categoryitems.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine1

DBSession = scoped_session(sessionmaker(bind=engine1))
session = DBSession()


# To list all categories
@app.route('/')
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    return render_template('categories.html', categories=categories)


# To list all category items
@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/items')
def showCategoryItems(category_id):
    category = session.query(Category).filter_by(id=category_id).one_or_none()
    items = session.query(CategoryItem).filter_by(
        category_id=category_id).all()
    return render_template('categoryItems.html',
                           categoryItems=items, category=category)


# To add new category, requires authenticated user
@app.route('/categories/add', methods=['GET', 'POST'])
@login_required
def addCategory():
    if request.method == 'GET':
        return render_template('addCategories.html')
    else:
        category = Category(name=request.form['categoryName'])
        session.add(category)
        session.commit()
        flash('Added Category Successfully!!')
        return redirect(url_for('showCategories'))


# To login into the application, Google auth
@app.route('/login/')
def login():
    print("Hitting Login")
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html',
                           client_id=GOOGLE_CLIENT_ID, STATE=state)


# To show item from a particular category
@app.route('/categories/<int:category_id>/items/<int:item_id>')
def showItem(category_id, item_id):
    item = session.query(CategoryItem).filter_by(id=item_id).one_or_none()
    return render_template('itemDesc.html', item=item)


# To edit item, requires authenticated user
@app.route('/categories/<int:category_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editItem(category_id, item_id):
    categories = session.query(Category).order_by(asc(Category.name))
    item = session.query(CategoryItem).filter_by(id=item_id).one_or_none()
    if request.method == 'GET':
        return render_template('itemEdit.html',
                               categories=categories, item=item)
    else:
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category']:
            item.category_id = request.form['category']
        session.add(item)
        session.commit()
        flash('Item successfully updated!')
        return redirect(url_for('showItem',
                                category_id=item.category_id, item_id=item_id))


# To delete item, requires authenticated user
@app.route('/categories/<int:category_id>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteItem(category_id, item_id):
    item = session.query(CategoryItem).filter_by(id=item_id).one_or_none()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Item successfully deleted!")
        return redirect(url_for('showCategories'))
    else:
        return render_template('delete.html', item=item)


# To add item to a particular category, requires authenticated user
@app.route('/categories/<int:category_id>/items/add', methods=['GET', 'POST'])
@login_required
def addItem(category_id):
    if request.method == 'GET':
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template('addItem.html',
                               categories=categories, category_id=category_id)
    else:
        selCategory = session.query(Category).filter_by(
            id=request.form['category']).one_or_none()
        item = CategoryItem(name=request.form['name'],
                            description=request.form['description'],
                            category=selCategory)
        session.add(item)
        session.commit()
        flash('Added Item Successfully!!')
        return redirect(url_for('showCategoryItems',
                                category_id=item.category_id))


# Return JSON of all the categories in the catalog.
@app.route('/categories/JSON')
def categories_json():
    categories = session.query(Category).all()
    return jsonify(categories=[i.serialize for i in categories])


# Return JSON of a particular item.
@app.route('/categories/<int:category_id>/items/<int:item_id>/JSON')
def categoryItems_json(category_id, item_id):
    items = session.query(CategoryItem).filter_by(id=item_id).one_or_none()
    return jsonify(items=[items.serialize])


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(
        email=login_session['email']).one_or_none()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one_or_none()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one_or_none()
        return user.id
    except:
        return None


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    # User Helper Functions
    return render_template('categories.html')


@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print(access_token)
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print(result)
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        # response = make_response(
        # json.dumps('Successfully disconnected.'), 200)
        # response.headers['Content-Type'] = 'application/json'
        response = redirect(url_for('showCategories'))
        flash("You are now logged out.")
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'))
        response.headers['Content-Type'] = 'application/json'
        return response


@login_manager.user_loader
def load_user(user_id):
    user = session.query(User).filter_by(id=user_id).one_or_none()
    return user


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
