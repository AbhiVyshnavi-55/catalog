from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Creating_Channel import Base, LanguageName, ChannelName, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///channel.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Language"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
abc_first = session.query(LanguageName).all()


# login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    abc_first = session.query(LanguageName).all()
    lmn = session.query(ChannelName).all()
    return render_template('login.html',
                           STATE=state, abc_first=abc_first, lmn=lmn)
    # return render_template('myhome.html', STATE=state
    # abc_first=abc_first,lmn=lmn)


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
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    User1 = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(User1)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

#####
# Home


@app.route('/')
@app.route('/home')
def home():
    abc_first = session.query(LanguageName).all()
    return render_template('myhome.html', abc_first=abc_first)

#####
# Language Category for admins


@app.route('/LanguageHub')
def LanguageHub():
    try:
        if login_session['username']:
            name = login_session['username']
            abc_first = session.query(LanguageName).all()
            abc = session.query(LanguageName).all()
            lmn = session.query(ChannelName).all()
            return render_template('myhome.html', abc_first=abc_first,
                                   abc=abc, lmn=lmn, uname=name)
    except:
        return redirect(url_for('showLogin'))

######
# Showing Language based on Language category


@app.route('/LanguageHub/<int:ghid>/AllLanguages')
def showLanguages(ghid):
    if 'username' in login_session:
        abc_first = session.query(LanguageName).all()
        abc = session.query(LanguageName).filter_by(id=ghid).one()
        lmn = session.query(ChannelName).filter_by(languagenameid=ghid).all()
        try:
            if login_session['username']:
                return render_template('showLanguages.html',
                                       abc_first=abc_first,
                                       abc=abc, lmn=lmn,
                                       uname=login_session['username'])
        except:
            return render_template('showLanguages.html',
                                   abc_first=abc_first, abc=abc, lmn=lmn)
    else:
        flash("You must login first to read")
        return render_template('login.html')

#####
# Add New Language


@app.route('/LanguageHub/addLanguageName', methods=['POST', 'GET'])
def addLanguageName():
    if 'username' in login_session:
        if request.method == 'POST':
            languagename = LanguageName(name=request.form['name'],
                                        user_id=login_session['user_id'])
            session.add(languagename)
            session.commit()
            return redirect(url_for('LanguageHub'))
        else:
            return render_template('addLanguageName.html', abc_first=abc_first)
    else:
        flash("You must login first to add new language")
        return render_template('login.html')

########
# Edit Language Category


@app.route('/LanguageHub/<int:ghid>/edit', methods=['POST', 'GET'])
def editLanguageName(ghid):
    if 'username' in login_session:
        editLanguageName = session.query(LanguageName).filter_by(id=ghid).one()
        creator = getUserInfo(editLanguageName.user_id)
        user = getUserInfo(login_session['user_id'])
    # If logged in user != channel owner redirect them
        if creator.id != login_session['user_id']:
            flash("You cannot edit this LanguageName."
                  "This is belongs to %s" % creator.name)
            return redirect(url_for('LanguageHub'))
        if request.method == "POST":
            if request.form['name']:
                editLanguageName.name = request.form['name']
            session.add(editLanguageName)
            session.commit()
            flash("editLanguageName Edited Successfully")
            return redirect(url_for('LanguageHub'))
        # abc_first is global variable we can them in entire application
        else:
            return render_template('editLanguageName.html',
                                   gh=editLanguageName,
                                   abc_first=abc_first)
    else:
        flash("You must login first in order to edit language ")
        return render_template('login.html')

######
# Delete Language Category


@app.route('/LanguageHub/<int:ghid>/delete', methods=['POST', 'GET'])
def deleteLanguageName(ghid):
    if 'username' in login_session:
        gh = session.query(LanguageName).filter_by(id=ghid).one()
        creator = getUserInfo(gh.user_id)
        user = getUserInfo(login_session['user_id'])
        # If logged in user != channel owner redirect them
        if creator.id != login_session['user_id']:
            flash("You cannot Delete this deleteLanguageName."
                  "This is belongs to %s" % creator.name)
            return redirect(url_for('LanguageHub'))
        if request.method == "POST":
            session.delete(gh)
            session.commit()
            flash("LanguageName Deleted Successfully")
            return redirect(url_for('LanguageHub'))
        else:
            return render_template('deleteLanguageName.html',
                                   gh=gh, abc_first=abc_first)
    else:
        flash("You must login first to delete language")
        return render_template('login.html')
# Add New channels Name Details


@app.route('/LanguageHub/addLanguageName/addLanguageDetails/'
           '<string:ghname>/add', methods=['GET', 'POST'])
def addLanguageDetails(ghname):
    if 'username' in login_session:
        abc = session.query(LanguageName).filter_by(name=ghname).one()
        # See if the logged in user is not the owner of Language
        creator = getUserInfo(abc.user_id)
        user = getUserInfo(login_session['user_id'])
        # If logged in user != channel owner redirect them
        if creator.id != login_session['user_id']:
            flash("You can't add new channel edition"
                  "This is belongs to %s" % creator.name)
            return redirect(url_for('showLanguages', ghid=abc.id))
        if request.method == 'POST':
            name = request.form['name']
            owner = request.form['owner']
            price = request.form['price']
            rating = request.form['rating']
            channeldetails = ChannelName(name=name, owner=owner,
                                         price=price, rating=rating,
                                         date=datetime.datetime.now(),
                                         languagenameid=abc.id,
                                         user_id=login_session['user_id'])
            session.add(channeldetails)
            session.commit()
            return redirect(url_for('showLanguages', ghid=abc.id))
        else:
            return render_template('addLanguageDetails.html',
                                   ghname=abc.name, abc_first=abc_first)
    else:
        flash("You must login first to add language details")
        return render_template('login.html')

######
# Edit channels details


@app.route('/LanguageHub/<int:ghid>/<string:ghename>/edit',
           methods=['GET', 'POST'])
def editLanguageChannel(ghid, ghename):
    if 'username' in login_session:
        gh = session.query(LanguageName).filter_by(id=ghid).one()
        channeldetails = session.query(
            ChannelName).filter_by(name=ghename).one()
        # See if the logged in user is not the owner of Language
        creator = getUserInfo(gh.user_id)
        user = getUserInfo(login_session['user_id'])
        # If logged in user != channel owner redirect them
        if creator.id != login_session['user_id']:
            flash("You can't edit this channel edition"
                  "This is belongs to %s" % creator.name)
            return redirect(url_for('showLanguages', ghid=gh.id))
        # POST methods
        if request.method == 'POST':
            channeldetails.name = request.form['name']
            channeldetails.owner = request.form['owner']
            channeldetails.price = request.form['price']
            channeldetails.rating = request.form['rating']
            channeldetails.date = datetime.datetime.now()
            session.add(channeldetails)
            session.commit()
            flash("Channel Edited Successfully")
            return redirect(url_for('showLanguages', ghid=ghid))
        else:
            return render_template('editLanguageChannel.html',
                                   ghid=ghid, channeldetails=channeldetails,
                                   abc_first=abc_first)
    else:
        flash("You must login first to edit channel details.")
        return render_template('login.html')

#####
# Delte channels details


@app.route('/LanguageHub/<int:ghid>/<string:ghename>/delete',
           methods=['GET', 'POST'])
def deleteLanguageChannel(ghid, ghename):
    if 'username' in login_session:
        gh = session.query(LanguageName).filter_by(id=ghid).one()
        channeldetails = session.query(
            ChannelName).filter_by(name=ghename).one()
        # See if the logged in user is not the owner of Language
        creator = getUserInfo(gh.user_id)
        user = getUserInfo(login_session['user_id'])
        # If logged in user != channel owner redirect them
        if creator.id != login_session['user_id']:
            flash("You can't delete this channel edition"
                  "This is belongs to %s" % creator.name)
            return redirect(url_for('showLanguages', ghid=gh.id))
        if request.method == "POST":
            session.delete(channeldetails)
            session.commit()
            flash("Deleted Channel Successfully")
            return redirect(url_for('showLanguages', ghid=ghid))
        else:
            return render_template('deleteLanguageChannel.html',
                                   ghid=ghid, channeldetails=channeldetails,
                                   abc_first=abc_first)
    else:
        flash("You must login first to delete channel details")
        return render_template('login.html')

####
# Logout from current user


@app.route('/logout')
def logout():
    if 'username' in login_session:
        access_token = login_session['access_token']
        print ('In gdisconnect access token is %s', access_token)
        print ('User name is: ')
        print (login_session['username'])
        if access_token is None:
            print ('Access Token is None')
            response = make_response(
                json.dumps('Current user not connected....'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        access_token = login_session['access_token']
        url = 'https://accounts.google.com/'
        'o/oauth2/revoke?token=%s' % access_token
        h = httplib2.Http()
        result = \
            h.request(uri=url, method='POST', body=None,
                      headers={'content-type':
                               'application/x-www-form-urlencoded'})[0]

        print (result['status'])
        if result['status'] == '200':
            del login_session['access_token']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            response = make_response(json.dumps(
                                                'Successfully disconnected'
                                                ), 200)
            response.headers['Content-Type'] = 'application/json'
            flash("Successful logged out")
            return redirect(url_for('showLogin'))
            # return response
        else:
            response = make_response(
                json.dumps('Failed to revoke token for given user.', 400))
            response.headers['Content-Type'] = 'application/json'
            return response
    else:
        flash("You must login first to perform the operations")
        return render_template('login.html')

#####
# initial json


@app.route('/LanguageHub/JSON')
def allLanguagesJSON():
    languagenames = session.query(LanguageName).all()
    category_dict = [c.serialize for c in languagenames]
    for c in range(len(category_dict)):
        languages = [i.serialize for i in session.
                     query(ChannelName).filter_by(languagenameid=category_dict
                                                  [c]["id"]
                                                  ).all()]
        if languages:
            category_dict[c]["language"] = languages
    return jsonify(LanguageName=category_dict)

####


# json path to language hub
@app.route('/LanguageHub/languagename/JSON')
def categoriesJSON():
    languages = session.query(LanguageName).all()
    return jsonify(languageName=[c.serialize for c in languages])

####


# json path to channels names
@app.route('/LanguageHub/languages/JSON')
def channelsJSON():
    channels = session.query(ChannelName).all()
    return jsonify(languages=[i.serialize for i in channels])

#####


# json for path to languages
@app.route('/LanguageHub/<path:language_name>/languages/JSON')
def categoryChannelsJSON(language_name):
    languageName = session.query(LanguageName).filter_by(
                                name=language_name
                                ).one()
    languages = session.query(ChannelName).filter_by(
                languagename=languageName).all()
    return jsonify(languageName=[i.serialize for i in languages])

#####


# final json app.route
@app.route('''/LanguageHub/<path:language_name>/<path:channel_name>/JSON''')
def ChannelJSON(language_name, channel_name):
    languageName = session.query(LanguageName).filter_by(
                                                         name=language_name
                                                         ).one()
    languageChannelName = session.query(ChannelName).filter_by(
           name=channel_name, languagename=languageName).one()
    return jsonify(languageChannelName=[languageChannelName.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=9000)
# THE END
