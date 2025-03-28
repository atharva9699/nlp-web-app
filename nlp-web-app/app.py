from flask import Flask, render_template, request, redirect
from db import Database
import spacy
from textblob import TextBlob  # For Sentiment Analysis

app = Flask(__name__)
dbo = Database()

# Load spaCy NER model
nlp = spacy.load("en_core_web_sm")

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/perform_registration', methods=['POST'])
def perform_registration():
    """Handles user registration."""
    name = request.form.get('user_name')
    email = request.form.get('user_email')
    password = request.form.get('user_password')

    response = dbo.insert(name, email, password)

    if response:
        return render_template('login.html', message="Registration Successful")
    else:
        return render_template("register.html", message="Email already exists")

@app.route('/perform_login', methods=['POST'])
def perform_login():
    """Handles user login."""
    email = request.form.get('user_email')
    password = request.form.get('user_password')

    response = dbo.search(email, password)

    if response:
        return redirect('/profile')
    else:
        return render_template('login.html', error='Incorrect email/password')

@app.route('/profile')
def profile():
    """User profile page with options for NLP tasks."""
    return render_template('profile.html')

# ------------------------ Named Entity Recognition (NER) ------------------------

@app.route('/ner')
def ner():
    return render_template('ner.html')

@app.route('/perform_ner', methods=['POST'])
def perform_ner():
    """Performs Named Entity Recognition (NER) on input text."""
    text = request.form.get('ner_text')

    if not text:
        return render_template('ner.html', error="Please enter some text.")

    # Perform NER
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    return render_template("ner.html", text=text, entities=entities)

# ------------------------ Sentiment Analysis ------------------------

@app.route('/sentiment_analysis')
def sentiment_analysis():
    return render_template("sentiment_analysis.html")

@app.route("/perform_sentiment", methods=["POST"])
def perform_sentiment():
    """Performs sentiment analysis on input text."""
    text = request.form.get("sentiment_text")

    if not text:
        return render_template("sentiment_analysis.html", error="Please enter some text.")

    # Perform Sentiment Analysis
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity

    # Classify sentiment
    if polarity > 0:
        sentiment = "Positive 😊"
    elif polarity < 0:
        sentiment = "Negative 😠"
    else:
        sentiment = "Neutral 😐"

    return render_template("sentiment_analysis.html", text=text, sentiment=sentiment, polarity=polarity)

# Route to render abuse detection page
@app.route('/abuse_detection')
def abuse_detection():
    return render_template("abuse_detection.html")

# Route to handle form submission and detect abuse
@app.route("/perform_abuse_detection", methods=["POST"])
def perform_abuse_detection():
    """Detects abusive language in input text."""
    text = request.form.get("abuse_text")

    if not text:
        return render_template("abuse_detection.html", error="Please enter some text.")

    # List of abusive words (extend this list for better accuracy)
    ABUSIVE_WORDS = ["stupid", "idiot", "dumb", "hate", "loser", "fool", "trash"]

    # Check for abusive words
    detected_words = [word for word in ABUSIVE_WORDS if word in text.lower()]

    if detected_words:
        result = f"❌ Abusive Content Detected! (Words: {', '.join(detected_words)})"
    else:
        result = "✅ Clean Content"

    return render_template("abuse_detection.html", text=text, result=result)



if __name__ == "__main__":
    app.run(debug=True)
