import feedparser
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rss.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define keywords to filter
KEYWORDS = ["Patch", "Expansion", "Hotfix", "Auction House", "Professions"]

# Database model
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    link = db.Column(db.String(300))
    published = db.Column(db.DateTime)

# Fetch and store RSS feed
def fetch_feed():
    feed = feedparser.parse("https://www.wowhead.com/news/rss")
    for entry in feed.entries:
        if any(keyword.lower() in entry.title.lower() for keyword in KEYWORDS):
            # Check for duplicates
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
def index():
    articles = Article.query.order_by(Article.published.desc()).all()
    return render_template('index.html', articles=articles)

# Trigger manual refresh (for testing)
@app.route('/refresh')
def refresh():
    fetch_feed()
    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    fetch_feed()
    app.run(debug=True)
