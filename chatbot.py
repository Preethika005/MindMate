import streamlit as st
import time
import requests
import json
import random
import string
from rapidfuzz import process, fuzz
from googletrans import Translator

translator = Translator()
awaiting_tips_response = False
current_emotion_for_tips = None

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


# --- Custom bubble styles ---
st.markdown("""
<style>
body { background-color: #f5f7fa; }
.chat-bubble {
    padding: 10px 15px;
    border-radius: 15px;
    margin-bottom: 10px;
    max-width: 80%;
    font-size: 16px;
    line-height: 1.4;
}
.user-bubble { background-color: #DCF8C6; margin-left: auto; margin-right: 0; }
.bot-bubble { background-color: #e6e6e6; margin-left: 0; margin-right: auto; }
.typing { font-style: italic; color: gray; margin: 5px 0 10px 0; }
</style>
""", unsafe_allow_html=True)

st.title("🧠 MindMate Mental Health Chatbot")

# --- Session state ---
if "messages" not in st.session_state:
    # Load replies file once for greeting
    with open("replies.json", "r", encoding="utf-8") as f:
        RESPONSES = json.load(f)

    # Pick a random greeting from the greetings list
    first_message = random.choice(RESPONSES.get("greetings", ["Hi, I'm MindMate! How are you feeling today?"]))
    
    st.session_state.messages = [
        {"role": "bot", "content": first_message}
    ]
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

# --- User input ---
user_input = st.chat_input("Type your message...")
if user_input:
    # Translate user input to English if needed
    if user_lang_code != "en":
        translated_input = translator.translate(user_input, src=user_lang_code, dest='en').text
    else:
        translated_input = user_input

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.typing = True
    st.session_state.translated_input = translated_input
    st.rerun()

with open("tips.json", "r", encoding="utf-8") as f:
    TIPS = json.load(f)

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
        text_clean, faq_keys_clean, scorer=fuzz.ratio, score_cutoff=85  # increased threshold
    )

    if result:
        best_match, score, idx = result

        # Additional safety check: ensure words are not too different
        if abs(len(text_clean) - len(faq_keys_clean[idx])) > 5:
            return None

        return MENTAL_HEALTH_QA[faq_keys[idx]]
    return None

# --- Predefined greetings and factual questions ---
greetings = ["hi", "hello", "hey", "good morning", "good evening","hey there","what's up"]

# --- Question detection ---
QUESTION_WORDS = ["what", "how", "why", "when", "where", "who", "which","can", "could", "should", "is", "are", "do", 
                  "does","did", "will", "would", "may", "might", "shall", "am", "have", "has", "had", "must", "need",
                  "want", "tell", "explain", "define","describe", "elaborate", "clarify","list", "compare", "contrast",
                    "summarize", "outline", "review", "analyze", "interpret"]

def is_question(text: str) -> bool:
    text_clean = clean_text(text)
    return (
        text_clean.endswith("?") or
        any(text_clean.startswith(word + " ") for word in QUESTION_WORDS)
    )

# --- Global session flags for tips ---
if "awaiting_tips_response" not in st.session_state:
    st.session_state.awaiting_tips_response = False
if "current_emotion_for_tips" not in st.session_state:
    st.session_state.current_emotion_for_tips = None

# --- Mapping emotions to replies.json keys ---
emotion_messages = {
    "sadness": "emotion_sadness",
    "anger": "emotion_anger",
    "joy": "emotion_joy",
    "fear": "emotion_fear",
    "stress": "stress_high",
    "anxiety": "emotion_sadness"  # fallback example
}

tips_prompts = [
    "Would you like some gentle tips to help you feel better? (yes/no)",
    "Can I share some tips that might brighten your day? (yes/no)",
    "How about a few helpful suggestions to ease your feelings? (yes/no)",
    "Would you like me to share some comforting advice? (yes/no)",
    "Can I offer a few tips to support you right now? (yes/no)"
]


# --- Generate bot reply ---
def generate_bot_reply(text: str):
    text_clean = clean_text(text)

    # Step 0: Crisis Detection
    crisis_phrases = ["kill myself", "suicide", "i want to die", "hurt myself", "can't go on"]
    if any(phrase in text_clean for phrase in crisis_phrases):
        return "It sounds like you are going through an extremely difficult time right now..."

    # Step 1: Check if awaiting tips response
    if st.session_state.awaiting_tips_response:
        user_lower = text_clean.lower()
        yes_responses = ["yes", "yeah", "yep", "sure"]
        no_responses = ["no", "nope", "nah", "not now"]

        if any(word in user_lower for word in yes_responses):
            tips_list = TIPS.get(st.session_state.current_emotion_for_tips, ["Take care of yourself 💙"])
            # Reset flags before returning
            st.session_state.awaiting_tips_response = False
            st.session_state.current_emotion_for_tips = None
            return "Here are some tips for you:\n\n- " + "\n- ".join(tips_list)

        elif any(word in user_lower for word in no_responses):
            # Reset flags before returning
            st.session_state.awaiting_tips_response = False
            st.session_state.current_emotion_for_tips = None
            return "Sure 💙 I'm here to listen whenever you need."

        else:
            return "I'm here whenever you're ready 💙."  # Keep waiting for a clear response

    # Step 2: Check if it's a question (FAQ)
    if is_question(text):
        faq_reply = get_faq_reply(text)
        if faq_reply:
            return faq_reply
        else:
            return "Sorry, I'm not sure about that 💙"

    # Step 3: Greetings
    if any(word in greetings for word in text_clean.split()):
        return get_random_reply("greetings")

    # Step 4: Emotion detection API call
    try:
        response = requests.post("http://127.0.0.1:5000/predict", json={"text": text}, timeout=5)
        data = response.json()
        emotion = data.get("emotion", "neutral")
        stress = data.get("stress", "low")
        urgency = data.get("urgency", "low")

        summary = f"Emotion: {emotion.capitalize()} || Stress: {stress.capitalize()} || Urgency: {urgency.capitalize()}"
        message_key = emotion_messages.get(emotion, "default")
        message = get_random_reply(message_key)

        # Ask if user wants tips for detected emotion
        if emotion in TIPS:
            st.session_state.awaiting_tips_response = True
            st.session_state.current_emotion_for_tips = emotion
            message += "\n\n💬 " + random.choice(tips_prompts)

        return f"{summary}\n\n {message}"

    except Exception:
        return "Sorry, I'm having trouble understanding right now. Please try again later 💙"


# --- Generate bot reply if needed ---
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