import streamlit as st
import random
import re

# -------------------------------
# TITLE AND DESCRIPTION
# -------------------------------
st.set_page_config(page_title="Customer Service Chatbot", page_icon="💬", layout="centered")
st.title("💬 Customer Service Chatbot")
st.write("Ask me anything about your order, refund, payment, or shipping!")

# -------------------------------
# INTENT DEFINITIONS
# -------------------------------
intents = {
    "greeting": {
        "keywords": ["hi", "hello", "hey"],
        "responses": [
            "Hello! 👋 How can I help you today?",
            "Hey there! 😊 What can I do for you?"
        ]
    },
    "goodbye": {
        "keywords": ["bye", "goodbye", "see you"],
        "responses": [
            "Goodbye! Have a great day! 👋",
            "See you soon! 😊"
        ]
    },
    "thanks": {
        "keywords": ["thanks", "thank you"],
        "responses": [
            "You're welcome! 😊",
            "Happy to help! 👍"
        ]
    },
    "order_status": {
        "keywords": ["order", "where is my order", "track order", "order id"],
        "responses": [
            "Please check your 'My Orders' page for live order tracking. 🚚",
            "Your order is being processed. You can track it from the Orders section. 📦",
            "To track an order, go to 'My Orders' → Select your order → Click 'Track'."
        ]
    },
    "refund": {
        "keywords": ["refund", "return", "money back"],
        "responses": [
            "To request a refund, visit the 'Orders' page and select 'Request Refund'. 💸",
            "Refunds are processed within 5–7 business days after approval."
        ]
    },
    "shipping": {
        "keywords": ["shipping", "delivery", "courier", "ship"],
        "responses": [
            "Standard delivery takes 3–5 business days. 🚚",
            "We offer free shipping for orders above ₹999!"
        ]
    },
    "payment": {
        "keywords": ["payment", "card", "upi", "credit", "debit"],
        "responses": [
            "We accept cards, UPI, and net banking. All transactions are secure. 🔒",
            "If your payment failed, please retry after a few minutes."
        ]
    },
    "default": {
        "responses": [
            "I'm not sure I understand that. Could you please rephrase?",
            "Hmm 🤔 I don’t have information on that. Can you ask about orders, refunds, or shipping?"
        ]
    }
}

# -------------------------------
# FUNCTION TO DETECT INTENT
# -------------------------------
def get_intent(user_input):
    user_input = user_input.lower()
    for intent, data in intents.items():
        for kw in data["keywords"]:
            if re.search(rf"\b{kw}\b", user_input):
                return intent
    return "default"

# -------------------------------
# FUNCTION TO GENERATE RESPONSE
# -------------------------------
def get_response(intent):
    return random.choice(intents[intent]["responses"])

# -------------------------------
# CHAT UI
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# User input
user_input = st.chat_input("Type your message here...")

if user_input:
    intent = get_intent(user_input)
    response = get_response(intent)
    st.session_state["chat_history"].append(("user", user_input))
    st.session_state["chat_history"].append(("bot", response))

# Display chat history
for sender, msg in st.session_state["chat_history"]:
    if sender == "user":
        st.markdown(f"🧑 **You:** {msg}")
    else:
        st.markdown(f"🤖 **Bot:** {msg}")
