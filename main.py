import random
import string

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration for SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# URL model to store the long and short URLs
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(200), nullable=False)
    short_url = db.Column(db.String(100), unique=True, nullable=False)

# Generate short URL
def generate_short_url(length=6):
    chars = string.ascii_letters + string.digits
    short_url = "".join(random.choice(chars) for _ in range(length))
    return short_url

@app.route("/", methods=["GET", "POST"])
def index():
    short_url = None
    if request.method == "POST":
        long_url = request.form['long_url']

        # Generate unique short URL
        short_url = generate_short_url()
        while URL.query.filter_by(short_url=short_url).first():
            short_url = generate_short_url()

        # Save URLs to the database
        new_url = URL(long_url=long_url, short_url=short_url)
        db.session.add(new_url)
        db.session.commit()

        # Create full short URL with domain
        short_url = f"{request.url_root}{short_url}"

    return render_template("index.html", short_url=short_url)

@app.route("/<short_url>")
def redirect_url(short_url):
    url = URL.query.filter_by(short_url=short_url).first()
    if url:
        return redirect(url.long_url)
    else:
        return "Short URL not found (404 error)", 404

if __name__ == "__main__":
    with app.app_context():  # Wrap create_all in app context
        db.create_all()
    app.run(debug=True)
