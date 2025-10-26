import streamlit as st
import random

# -------------------------------
# TITLE AND DESCRIPTION
# -------------------------------
st.set_page_config(page_title="Customer Service Chatbot", page_icon="💬", layout="centered")
st.title("💬 Customer Service Chatbot")
st.write("Ask me anything about our products, services, or policies!")

# -------------------------------
# SIMPLE RULE-BASED RESPONSES
# -------------------------------
responses = {
    "hi": ["Hello! 👋 How can I help you today?", "Hey there! What can I do for you?"],
    "hello": ["Hi there! 😊 How may I assist you?", "Hello! How can I help you today?"],
    "bye": ["Goodbye! Have a nice day! 👋", "See you soon! 😊"],
    "thanks": ["You're welcome! 😊", "Happy to help! 👍"],
    "product": [
        "We offer a variety of products. Could you specify which category you’re interested in?",
        "Our products include electronics, fashion, and home essentials. What are you looking for?"
    ],
    "refund": [
        "To request a refund, please visit the 'Orders' section in your account and click 'Request Refund'.",
        "Refunds are processed within 5-7 business days after approval."
    ],
    "shipping": [
        "Shipping usually takes 3-5 business days. 🚚",
        "We provide free shipping for orders above ₹999!"
    ],
    "payment": [
        "We accept payments via credit/debit cards, UPI, and net banking.",
        "Your payment details are always encrypted and secure 🔒."
    ],
    "default": [
        "I'm not sure I understand that. Could you please rephrase?",
        "Hmm 🤔 I don’t have information on that. Can you ask about products, refunds, or shipping?"
    ]
}

# -------------------------------
# FUNCTION TO GENERATE RESPONSE
# -------------------------------
def get_response(user_input):
    user_input = user_input.lower()
    for key in responses.keys():
        if key in user_input:
            return random.choice(responses[key])
    return random.choice(responses["default"])

# -------------------------------
# CHAT UI
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# User input
user_input = st.chat_input("Type your message here...")

if user_input:
    response = get_response(user_input)
    st.session_state["chat_history"].append(("user", user_input))
    st.session_state["chat_history"].append(("bot", response))

# Display chat history
for sender, msg in st.session_state["chat_history"]:
    if sender == "user":
        st.markdown(f"🧑 **You:** {msg}")
    else:
        st.markdown(f"🤖 **Bot:** {msg}")
