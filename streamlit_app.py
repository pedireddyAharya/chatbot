# streamlit_app.py
import streamlit as st
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import os

# Ensure NLTK tokenizer resources (first run will download)
nltk_packages = ["punkt", "stopwords"]
for pkg in nltk_packages:
    try:
        nltk.data.find(f"tokenizers/{pkg}")
    except:
        nltk.download(pkg)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# ---------- Helpers ----------
@st.cache_data
def load_intents(path="intents.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_orders(path="orders.csv"):
    if os.path.exists(path):
        return pd.read_csv(path, dtype=str)
    else:
        return pd.DataFrame(columns=["order_id", "customer_name", "status", "eta"])

def preprocess_text(text):
    # simple tokenization + lowercase + remove stopwords
    text = str(text).lower()
    tokens = word_tokenize(text)
    stops = set(stopwords.words("english"))
    tokens = [t for t in tokens if t.isalnum() and t not in stops]
    return " ".join(tokens)

# Build TF-IDF matrix for all example patterns
@st.cache_data
def build_vectorizer(intents):
    patterns = []
    tags = []
    for intent in intents["intents"]:
        for p in intent["patterns"]:
            patterns.append(preprocess_text(p))
            tags.append(intent["tag"])
    vect = TfidfVectorizer()
    X = vect.fit_transform(patterns)
    return vect, X, patterns, tags

# Get best intent from user input using cosine similarity
def predict_intent(user_text, vect, X, tags, threshold=0.35):
    user_proc = preprocess_text(user_text)
    if user_proc.strip() == "":
        return None, 0.0
    user_vec = vect.transform([user_proc])
    sims = cosine_similarity(user_vec, X).flatten()
    best_idx = sims.argmax()
    best_score = sims[best_idx]
    if best_score >= threshold:
        return tags[best_idx], float(best_score)
    return None, float(best_score)

# Fallback handler
def fallback_response():
    return "Sorry, I didn't quite get that. Can you rephrase or provide your order ID?"

# ---------- UI ----------
st.set_page_config(page_title="Customer Support Chatbot", layout="centered")
st.title("🛎️ Customer Support Chatbot (Streamlit)")

st.markdown(
    """
Simple customer service bot with two modes:
- **Rule-based** (fast, keyword matching)
- **NLP-based** (TF-IDF + cosine similarity on example phrases)
"""
)

# Load data
intents = load_intents()
orders_df = load_orders()
vect, X, patterns, tags = build_vectorizer(intents)

# Sidebar controls
st.sidebar.header("Bot settings")
mode = st.sidebar.selectbox("Mode", ["NLP (TF-IDF)", "Rule-based"])
threshold = st.sidebar.slider("NLP confidence threshold", 0.1, 0.8, 0.35, 0.05)
st.sidebar.markdown("Tip: Lower threshold → more matches, higher → stricter matching.")

# Chat area
if "history" not in st.session_state:
    st.session_state.history = []

def append_history(sender, text):
    st.session_state.history.append({"sender": sender, "text": text})

# Show history
for msg in st.session_state.history:
    if msg["sender"] == "user":
        st.markdown(f"**You:** {msg['text']}")
    else:
        st.markdown(f"**Bot:** {msg['text']}")

# Input area
user_input = st.text_input("Type your message here...")

if st.button("Send") or (user_input and st.session_state.get("auto_send", False)):
    if not user_input:
        st.warning("Enter a message.")
    else:
        append_history("user", user_input)

        # RULE-BASED logic (simple)
        def rule_based_response(text):
            t = text.lower()
            if any(k in t for k in ["where is my order", "track", "order status", "order id"]):
                return "Please provide your order ID (e.g., OD1001)."
            if "cancel" in t and "order" in t:
                return "You can cancel your order before it is shipped. Share the order ID to check."
            if "return" in t:
                return "You can return items within 7 days of delivery. Would you like the return policy link?"
            if "shipping" in t or "delivery" in t:
                return "Free shipping for orders above ₹500. Do you have a specific order?"
            if any(k in t for k in ["human", "agent", "support", "representative"]):
                return "Connecting you to a human agent..."
            if any(k in t for k in ["hi", "hello", "hey"]):
                return "Hello! How can I help you?"
            if any(k in t for k in ["bye", "goodbye", "thanks", "thank you"]):
                return "Thanks for contacting us. Goodbye!"
            return None

        response = None

        if mode == "Rule-based":
            response = rule_based_response(user_input)
            if response is None:
                response = fallback_response()
        else:
            # NLP mode
            predicted_tag, score = predict_intent(user_input, vect, X, tags, threshold)
            if predicted_tag:
                # pick a response from intents
                for intent in intents["intents"]:
                    if intent["tag"] == predicted_tag:
                        response = f"{intent['responses'][0]} (intent: {predicted_tag}, conf={score:.2f})"
                        break
            else:
                # check if user provided an order id directly
                # small regex-like check: contains 'OD' followed by digits
                import re
                m = re.search(r"(OD\d{3,})", user_input.upper())
                if m:
                    order_id = m.group(1)
                    row = orders_df[orders_df["order_id"].str.upper() == order_id.upper()]
                    if not row.empty:
                        status = row.iloc[0]["status"]
                        eta = row.iloc[0]["eta"]
                        response = f"Order {order_id} status: {status}. ETA: {eta}."
                    else:
                        response = f"Order {order_id} not found. Please check the ID."
                else:
                    # fallback similarity to single pattern matches (lower threshold)
                    predicted_tag_low, score_low = predict_intent(user_input, vect, X, tags, threshold=0.15)
                    if predicted_tag_low:
                        for intent in intents["intents"]:
                            if intent["tag"] == predicted_tag_low:
                                response = f"{intent['responses'][0]} (intent: {predicted_tag_low}, conf={score_low:.2f})"
                                break
                    else:
                        response = fallback_response()

        append_history("bot", response)
        st.experimental_rerun()

# Small utility: quick order lookup box
st.divider()
st.subheader("Quick order lookup (simulate)")
lookup_id = st.text_input("Enter order ID (e.g., OD1001) to lookup", key="lookup")
if st.button("Lookup order"):
    if lookup_id.strip() == "":
        st.warning("Enter an order ID.")
    else:
        row = orders_df[orders_df["order_id"].str.upper() == lookup_id.upper()]
        if not row.empty:
            st.info(f"Order {lookup_id} — status: {row.iloc[0]['status']}, ETA: {row.iloc[0]['eta']}")
        else:
            st.error("Order not found.")

st.divider()
st.caption("This is a demo app. Extend by connecting to your real order DB or adding more intents.")

