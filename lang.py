import streamlit as st
import time
import requests
import json
import random
import string
from rapidfuzz import process, fuzz
from googletrans import Translator

# --- Translator setup ---
translator = Translator()

# --- Streamlit page config ---
st.set_page_config(page_title="MindMate Chatbot", page_icon="🧠")

# --- Language selection ---
if "language" not in st.session_state:
    st.session_state.language = "English"  # default

st.sidebar.title("🌐 Select Language")
st.session_state.language = st.sidebar.selectbox(
    "Choose your language:", ["English", "Hindi", "Spanish", "French", "German", "Telugu", "Tamil"]
)
LANG_CODES = {"English": "en", "Hindi": "hi", "Spanish": "es", "French": "fr", "German": "de", "Telugu": "te", "Tamil": "ta"}
user_lang_code = LANG_CODES[st.session_state.language]

# --- Chat bubble styles ---
st.markdown("""
<style>
body { background-color: #f5f7fa; }
.chat-bubble { padding: 10px 15px; border-radius: 15px; margin-bottom: 10px; max-width: 80%; font-size: 16px; line-height: 1.4; }
.user-bubble { background-color: #DCF8C6; margin-left: auto; margin-right: 0; }
.bot-bubble { background-color: #e6e6e6; margin-left: 0; margin-right: auto; }
.typing { font-style: italic; color: gray; margin: 5px 0 10px 0; }
</style>
""", unsafe_allow_html=True)

st.title("🧠 MindMate Mental Health Chatbot")

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "typing" not in st.session_state:
    st.session_state.typing = False

# --- Display chat messages ---
for msg in st.session_state.messages:
    bubble_class = "user-bubble" if msg["role"] == "user" else "bot-bubble"
    sender = "You" if msg["role"] == "user" else "MindMate"
    st.markdown(f"<div class='chat-bubble {bubble_class}'><b>{sender}:</b> {msg['content']}</div>", unsafe_allow_html=True)

# --- Typing indicator ---
if st.session_state.typing:
    st.markdown("<div class='typing'>MindMate is typing...</div>", unsafe_allow_html=True)

# --- Load motivational replies ---
with open("replies.json", "r", encoding="utf-8") as f:
    RESPONSES = json.load(f)

def get_random_reply(category: str) -> str:
    return random.choice(RESPONSES.get(category, RESPONSES["default"]))

# --- Load mental health FAQ ---
with open("mental_health_faq.json", "r", encoding="utf-8") as f:
    MENTAL_HEALTH_QA = json.load(f)

# --- Text cleaning function ---
def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

# --- Fuzzy FAQ matching ---
def get_faq_reply(user_input):
    text_clean = clean_text(user_input)
    faq_keys = list(MENTAL_HEALTH_QA.keys())
    faq_keys_clean = [clean_text(q) for q in faq_keys]

    result = process.extractOne(
        text_clean, faq_keys_clean, scorer=fuzz.ratio, score_cutoff=85
    )

    if result:
        best_match, score, idx = result
        if abs(len(text_clean) - len(faq_keys_clean[idx])) > 5:
            return None
        return MENTAL_HEALTH_QA[faq_keys[idx]]
    return None

# --- Predefined greetings and question detection ---
greetings = ["hi", "hello", "hey", "good morning", "good evening","hey there","what's up"]
QUESTION_WORDS = ["what", "how", "why", "when", "where", "who", "which","can", "could", "should", "is", "are", "do", 
                  "does","did", "will", "would", "may", "might", "shall", "am", "have", "has", "had", "must", "need",
                  "want", "tell", "explain", "define","describe", "elaborate", "clarify","list", "compare", "contrast",
                  "summarize", "outline", "review", "analyze", "interpret"]

def is_question(text: str) -> bool:
    text_clean = clean_text(text)
    return text_clean.endswith("?") or any(text_clean.startswith(word + " ") for word in QUESTION_WORDS)

# --- Generate bot reply ---
def generate_bot_reply(text: str):
    text_clean = clean_text(text)

    # Crisis detection
    crisis_phrases = [
        "kill myself", "end my life", "suicide", "want to die", "die by suicide",
        "hurt myself", "i will die", "can't go on", "no reason to live",
        "life is meaningless", "i want to end it", "take my life"," i want to kill myself",
        "i want to die", "i'm going to kill myself", "i'm going to die", "i want to harm myself",
        "i want to end my life", "i can't go on", "there's no point in living", "life is pointless",
        "i don't want to live anymore", "i'm done with life", "i want to end it all", "i'm so tired of living",
        "i want to disappear", "i'm at the end of my rope", "i can't take it anymore", "i'm overwhelmed and want to die"
    ]
    if any(phrase in text_clean for phrase in crisis_phrases):
        return (
            "💙 I'm really sorry that you're feeling like this. "
            "You don’t have to face it alone. Please reach out to someone who can help — "
            "**in India, you can call AASRA at +91-9820466726 or Snehi at +91-9582208181.**\n\n"
            "If you’re outside India, you can find international hotlines here: "
            "[findahelpline.com](https://findahelpline.com), available 24/7. "
            "You matter and help is available right now 💙."
        )

    # FAQ
    if is_question(text):
        faq_reply = get_faq_reply(text)
        if faq_reply:
            return faq_reply
        else:
            return "Sorry, I'm not sure about that 💙"

    # Greetings
    if any(greet in text_clean for greet in greetings):
        return get_random_reply("greetings")

    # Emotion/stress fallback
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
        return "Sorry, I'm having trouble understanding right now. Please try again later. 💙"

# --- User input handling with translation ---
user_input = st.chat_input("Type your message...")
if user_input:
    # Translate user input to English if needed
    if user_lang_code != "en":
        translated_input = translator.translate(user_input, src=user_lang_code, dest='en').text
    else:
        translated_input = user_input

    # Save original user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Typing state
    st.session_state.typing = True
    st.session_state.translated_input = translated_input
    st.rerun()

# --- Generate bot reply with translation ---
if st.session_state.typing and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    time.sleep(1.2)  # simulate typing
    last_user_text_en = st.session_state.translated_input
    bot_reply_en = generate_bot_reply(last_user_text_en)

    # Translate bot response to user language
    if user_lang_code != "en":
        bot_reply = translator.translate(bot_reply_en, src='en', dest=user_lang_code).text
    else:
        bot_reply = bot_reply_en

    st.session_state.messages.append({"role": "bot", "content": bot_reply})
    st.session_state.typing = False
    st.rerun()
