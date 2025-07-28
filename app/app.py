# CLI - export FLASK_APP=app.app (once)
# Run - flask run


# Railway:
# Root Directory: /app
# Custom Start Command: gunicorn app:app

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