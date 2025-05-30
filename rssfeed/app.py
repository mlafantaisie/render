import feedparser
import datetime
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from auth import check_password
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rss.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecretkey")
db = SQLAlchemy(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define keywords to filter
KEYWORDS = ["Patch", "Expansion", "Hotfix", "Auction House", "Professions"]

class User(UserMixin):
    id = 1  # Static user id, single user system

@login_manager.user_loader
def load_user(user_id):
    if user_id == "1":
        return User()
    return None

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    link = db.Column(db.String(300))
    published = db.Column(db.DateTime)

def fetch_feed():
    feed = feedparser.parse("https://www.wowhead.com/news/rss")
    for entry in feed.entries:
        if any(keyword.lower() in entry.title.lower() for keyword in KEYWORDS):
            if not Article.query.filter_by(link=entry.link).first():
                published_dt = datetime.datetime(*entry.published_parsed[:6])
                new_article = Article(
                    title=entry.title, 
                    link=entry.link, 
                    published=published_dt
                )
                db.session.add(new_article)
    db.session.commit()

@app.route('/')
@login_required
def index():
    articles = Article.query.order_by(Article.published.desc()).all()
    return render_template('index.html', articles=articles)

@app.route('/refresh')
@login_required
def refresh():
    fetch_feed()
    return redirect(url_for('index'))

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if check_password(username, password):
            user = User()
            login_user(user)
            return redirect(url_for('index'))
        return "Invalid credentials", 401
    return '''
        <form method="post">
            Username: <input type="text" name="username"/><br>
            Password: <input type="password" name="password"/><br>
            <input type="submit" value="Login"/>
        </form>
    '''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    fetch_feed()
    app.run(debug=True)
