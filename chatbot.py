import streamlit as st
import time
import requests
import json
import random
st.set_page_config(page_title="MindMate Chatbot", page_icon="🧠")

# --- Custom bubble styles ---
st.markdown("""
<style>
body {
    background-color: #f5f7fa;
}
.chat-bubble {
    padding: 10px 15px;
    border-radius: 15px;
    margin-bottom: 10px;
    max-width: 80%;
    font-size: 16px;
    line-height: 1.4;
}
.user-bubble {
    background-color: #DCF8C6;
    margin-left: auto;
    margin-right: 0;
}
.bot-bubble {
    background-color: #e6e6e6;
    margin-left: 0;
    margin-right: auto;
}
.typing {
    font-style: italic;
    color: gray;
    margin: 5px 0 10px 0;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 MindMate Mental Health Chatbot")

# --- Manage session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "typing" not in st.session_state:
    st.session_state.typing = False

# --- Render chat messages ---
for msg in st.session_state.messages:
    bubble_class = "user-bubble" if msg["role"] == "user" else "bot-bubble"
    sender = "You" if msg["role"] == "user" else "MindMate"
    st.markdown(f"<div class='chat-bubble {bubble_class}'><b>{sender}:</b> {msg['content']}</div>", unsafe_allow_html=True)

# --- Typing indicator ---
if st.session_state.typing:
    st.markdown("<div class='typing'>MindMate is typing...</div>", unsafe_allow_html=True)

# --- User input ---
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.typing = True
    st.rerun()

# Load replies from JSON
with open("replies.json", "r", encoding="utf-8") as f:
    RESPONSES = json.load(f)

def get_random_reply(category: str) -> str:
    return random.choice(RESPONSES.get(category, RESPONSES["default"]))

# --- Greeting & factual Q/A ---
greetings = ["hi", "hello", "hey", "good morning", "good evening"]
factual_questions = {
    "what is your name": "I'm MindMate, your mental health companion chatbot 💙",
    "who are you": "I'm MindMate, here to listen and support your mental health journey.",
    "what can you do": "I can understand your emotions and offer guidance, coping tips, and encouragement.",
    "who made you": "I was built with love to support people like you.",
    "how are you": "I'm just a chatbot, but I feel great when I can support you 💙. How are you today?"
}

# --- Rule-based response generator ---
def generate_bot_reply(text: str):
    text_lower = text.strip().lower()

    # Greetings
    if any(greet in text_lower for greet in ["hi", "hello", "hey", "good morning", "good evening"]):
        return get_random_reply("greetings")

    # Factual Q&A (unchanged)
    for q in factual_questions:
        if q in text_lower:
            return factual_questions[q]

    # API call
    try:
        response = requests.post("http://127.0.0.1:5000/predict", json={"text": text}, timeout=5)
        data = response.json()

        emotion = data.get("emotion", "neutral")
        stress = data.get("stress_level", "low")
        urgency = data.get("urgency", "low")

        if urgency == "high":
            return get_random_reply("urgency_high")
        if stress == "high":
            return get_random_reply("stress_high")
        if emotion == "joy":
            return get_random_reply("emotion_joy")
        if emotion == "sadness":
            return get_random_reply("emotion_sadness")
        if emotion == "anger":
            return get_random_reply("emotion_anger")

        return get_random_reply("default")

    except Exception:
        return "Sorry, I’m having trouble understanding right now. Please try again later. 💙"

# --- Generate bot reply if needed ---
if st.session_state.typing and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    time.sleep(1.2)  # simulate typing delay
    last_user_text = st.session_state.messages[-1]["content"]
    bot_reply = generate_bot_reply(last_user_text)
    st.session_state.messages.append({"role": "bot", "content": bot_reply})
    st.session_state.typing = False
    st.rerun()
