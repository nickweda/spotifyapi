# CLI - export FLASK_APP=app.app (once)
# Run - flask run

# Render - Free forever but autoshutsdown - takes a moment for the site to start - users see this - also slow
# Build Command: pip install -r app/requirements.txt
# Start Command: gunicorn app.app:app
# Add env variables

# Railway - 30 day free trial
# Root Directory: /app
# Custom Start Command: gunicorn app:app
# Add env variables

# Learning Takeaway: It costs money to rent a server for deployment

from flask import Flask, request, render_template

# Deployment - root app structure
try:
    from app.ml_utils import get_prediction
except:
    from ml_utils import get_prediction

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    features = None
    if request.method == "POST":
        # Get form input
        track_url = request.form.get("track_url")

        # Generate prediction - From ML Utils
        prediction, features = get_prediction(track_url)

    # To HTML
    return render_template("index.html", prediction=prediction, features=features)