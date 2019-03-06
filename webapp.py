from flask import Flask, redirect, url_for, session, request, jsonify, Markup
from flask_oauthlib.client import OAuth
from flask import render_template
import os
import json

app = Flask(__name__)
app.debug = True #Change this to False for production
os.system("echo [] >"+ myfile)
#remove vvv for production
#os.environ['OAUTHLIB_INSECURE_TRANSPORT']='1'
app.secret_key = os.environ['SECRET_KEY'] #used to sign session cookies
oauth = OAuth(app)

#Set up GitHub as OAuth provider
github = oauth.remote_app(
        'github',
        consumer_key=os.environ['GITHUB_CLIENT_ID'], #your web app's "username" for github's OAuth
        consumer_secret=os.environ['GITHUB_CLIENT_SECRET'],#your web app's "password" for github's OAuth
        request_token_params={'scope': 'user:email'}, #request read-only access to the user's email.  For a list of possible scopes, see developer.github.com/apps/building-oauth-apps/scopes-for-oauth-apps
        base_url='https://api.github.com/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://github.com/login/oauth/access_token',  
        authorize_url='https://github.com/login/oauth/authorize' #URL for github's OAuth login
        )

#with open(myfile, mode='r') as f:
#    data = json.load(f)

@app.context_processor
def inject_logged_in():
    return {"logged_in":('github_token' in session)}

@app.route('/')
def home():
    return render_template('home.html')

#the tokengetter is automatically called to check who is logged in.
@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')

if __name__ == '__main__':
    app.run()
