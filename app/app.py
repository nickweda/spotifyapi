# CLI - export FLASK_APP=app.app (once)
# Run - flask run

from flask import Flask, request, render_template
from app.ml_utils import get_prediction

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    if request.method == "POST":
        # Get form input
        track_url = request.form.get("track_url")

        # Generate prediction
        prediction = get_prediction(track_url)

    
    return render_template("index.html", prediction=prediction)