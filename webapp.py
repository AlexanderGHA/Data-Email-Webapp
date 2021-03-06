from flask import Flask, redirect, url_for, session, request, render_template
from flask_oauthlib.client import OAuth
import os

app = Flask(__name__)
app.debug = True #Change this to False for production
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

@app.context_processor
def inject_logged_in():
    return {"logged_in":('github_token' in session)}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login/post')
def data_post():
    return render_template('data_post.html')
    
@app.route('/anon')
def anon_post():
    return render_template('anon_post.html') 
        
@app.route('/login')
def login():   
    return github.authorize(callback=url_for('authorized', _external=True, _scheme='https')) #callback URL must match the pre-configured callback URL

@app.route('/logout')
def logout():
    session.clear()
    return render_template('home.html', message='You were logged out')

@app.route('/login/callback')
def authorized():
    resp = github.authorized_response()
    if resp is None:
        session.clear()
        message = 'Access denied: reason=' + request.args['error'] + ' error=' + request.args['error_description'] + ' full=' + pprint.pformat(request.args)      
    else:
        try:
            session['github_token'] = (resp['access_token'], '') #save the token to prove that the user logged in
            session['user_data']=github.get('user').data
            message='You were successfully logged in as ' + session['user_data']['login']
        except Exception as inst:
            session.clear()
            print(inst)
            message='Unable to login, please try again.  '
    return render_template('home.html', message=message)

#the tokengetter is automatically called to check who is logged in.
@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')

if __name__ == '__main__':
    app.run()
