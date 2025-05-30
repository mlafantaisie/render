import feedparser
import datetime
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from auth import check_password
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
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

def scrape_site():
    import sys

    URL = "https://www.wowhead.com/news"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (compatible; Bot/0.1; +https://example.com/bot)"
    }
    KEYWORDS = ["patch", "expansion", "hotfix", "auction", "profession"]

    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching WoWhead: {e}", file=sys.stderr)
        return

    soup = BeautifulSoup(response.text, "html.parser")
    
    # WoWhead's news list: articles are in divs with class "news-list"
    news_list = soup.find("div", class_="news-list")

    if not news_list:
        print("No news-list div found.", file=sys.stderr)
        return

    articles = news_list.find_all("article")

    new_articles = 0

    for article in articles:
        title_tag = article.find("h3")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link_tag = title_tag.find("a")
        link = f"https://www.wowhead.com{link_tag['href']}" if link_tag else None

        if any(keyword in title.lower() for keyword in KEYWORDS):
            if not Article.query.filter_by(link=link).first():
                new_article = Article(
                    title=title,
                    link=link,
                    published=datetime.datetime.utcnow()  # no real published date in listing
                )
                db.session.add(new_article)
                new_articles += 1
                print(f"Inserted: {title}", file=sys.stderr)

    db.session.commit()
    print(f"Scraping finished. New articles inserted: {new_articles}", file=sys.stderr)

@app.route('/')
@login_required
def index():
    articles = Article.query.order_by(Article.published.desc()).all()
    return render_template('index.html', articles=articles)

@app.route('/refresh', methods=["GET", "POST"])
@login_required
def refresh():
    scrape_site()
    return redirect(request.referrer or url_for('index'))

@app.route('/admin')
@login_required
def admin():
    articles = Article.query.order_by(Article.published.desc()).all()
    return render_template('admin.html', articles=articles)

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
