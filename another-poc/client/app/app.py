import os
from flask import Flask, url_for, session, redirect, render_template
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = '!secret'
# app.config.from_object('__main__.os.environ')

oauth = OAuth(app)
oauth.register(
    name='keycloak',
    client_id=os.getenv('OIDC_CLIENT_ID'),
    client_secret=os.getenv('OIDC_CLIENT_SECRET'),
    server_metadata_url=os.getenv('OIDC_DISCOVERY_URL'),
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@app.route('/')
def index():
    user = session.get('user')
    return render_template('index.html', user=user)


@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.keycloak.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    token = oauth.keycloak.authorize_access_token()
    session['user'] = token['userinfo']
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return render_template('profile.html', user=user)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)