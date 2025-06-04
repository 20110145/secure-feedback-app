import os
import csv
from flask import Flask, render_template, request, redirect, session, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# OAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id_, email):
        self.id = id_
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    user_data = session.get("user")
    if user_data and user_data["id"] == user_id:
        return User(user_data["id"], user_data["email"])
    return None

@app.route('/')
def index():
    return render_template('feedback_form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    with open('feedback.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, email, message])

    return redirect('/')

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')  # FIXED
    user_info = resp.json()

    if user_info['email'] != os.getenv('ADMIN_EMAIL'):
        return "Unauthorized", 403

    user = User(user_info['sub'], user_info['email'])  # use 'sub' instead of 'id'
    login_user(user)
    session["user"] = {"id": user_info['sub'], "email": user_info['email']}
    return redirect('/admin')


@app.route('/admin')
@login_required
def admin():
    with open('feedback.csv', newline='') as file:
        entries = list(csv.reader(file))
    return render_template('admin.html', entries=entries)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop("user", None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

