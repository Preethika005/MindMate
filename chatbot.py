import streamlit as st
import time
import requests
import json
import random
import string
from rapidfuzz import process, fuzz
from googletrans import Translator
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from collections import Counter
from reportlab.platypus import Spacer
from reportlab.platypus import Table

translator = Translator()
# awaiting_tips_response = False
# current_emotion_for_tips = None

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

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # store emotion, stress, message timeline


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

# def get_random_reply(category: str) -> str:
#     return random.choice(RESPONSES.get(category, RESPONSES["default"]))

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

def get_random_reply(category):
    return random.choice(RESPONSES.get(category, RESPONSES["default"]))


# --- Predefined greetings and factual questions ---
greetings = ["hi", "hello", "hey", "good morning", "good evening","hey there","what's up","hi there","greetings","howdy","hello there"]

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
    crisis_phrases = ["kill myself", "end my life", "suicide", "want to die", "die by suicide",
        "hurt myself", "i will die", "can't go on", "no reason to live",
        "life is meaningless", "i want to end it", "take my life"," i want to kill myself",
        "i want to die", "i'm going to kill myself", "i'm going to die", "i want to harm myself",
        "i want to end my life", "i can't go on", "there's no point in living", "life is pointless",
        "i don't want to live anymore", "i'm done with life", "i want to end it all", "i'm so tired of living",
        "i want to disappear", "i'm at the end of my rope", "i can't take it anymore", "i'm overwhelmed and want to die"
]
    if any(phrase in text_clean for phrase in crisis_phrases):
        return "It sounds like you are going through an extremely difficult time right now...You don’t have to face it alone. Please reach out to someone who can help."

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

        st.session_state.awaiting_tips_response = False
        st.session_state.current_emotion_for_tips = None
        
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

        # Store for report
        st.session_state.chat_history.append({"emotion": emotion, "stress": stress, "text": text})


        summary = f"Emotion: {emotion.capitalize()} || Stress: {stress.capitalize()} || Urgency: {urgency.capitalize()}"
        message_key = emotion_messages.get(emotion, "default")
        message = get_random_reply(message_key)

        # Ask if user wants tips for detected emotion
        if emotion in TIPS:
            st.session_state.awaiting_tips_response = True
            st.session_state.current_emotion_for_tips = emotion
            message += "\n\n💬 " + random.choice(tips_prompts)

        # return f"{summary}\n\n {message}"
        return f"\n {message}"

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

# ----------------- 📄 PDF Report Generation -----------------
class FooterCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw_footer(self):
        footer_text = "Generated by MindMate - Your AI Mental Health Companion "
        width, height = A4
        self.setFont("Helvetica-Oblique", 9)
        self.setFillColorRGB(0.5, 0.5, 0.5)
        self.drawCentredString(width / 2, 0.5 * inch, footer_text)

    def showPage(self):
        self.draw_footer()
        super().showPage()

    def save(self):
        self.draw_footer()
        super().save()


colored_title_style = ParagraphStyle(
    'ColoredTitle',
    fontName='Helvetica-Bold',
    fontSize=25,
    textColor=colors.HexColor("#1C77C3"),  # Soft blue, change as desired (example: "#0078D4" or "#4BA3C3")
    spaceAfter=16,
    alignment=1,  # Center the title
)

section_heading_style = ParagraphStyle(
    'SectionHeading',
    fontName='Times-Bold',
    fontSize=18,
    textColor=colors.HexColor("#1C77C3"),
    alignment=0,  # Left
    spaceBefore=18,    # Space above the paragraph
    spaceAfter=10,     # Space below the paragraph
)
times_normal_style = ParagraphStyle(
    'TimesNormal',
    fontName='Times-Roman',
    fontSize=12,           # You can adjust size as desired
)
summary_center_style = ParagraphStyle(
    'SummaryCenter',
    fontName='Times-Roman',
    fontSize=13,
    alignment=1,  # 1 means center
    spaceBefore=16,
    spaceAfter=10,
)

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from io import BytesIO
from collections import Counter
import matplotlib.pyplot as plt
from datetime import datetime

def generate_mindmate_report():
    filename = "MindMate_Report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    now = datetime.now().strftime("%B %d, %Y - %H:%M %p")

    # --- Styles ---
    colored_title_style = ParagraphStyle(
        'ColoredTitle',
        fontName='Helvetica-Bold',
        fontSize=25,
        textColor=colors.HexColor("#1C77C3"),
        alignment=1,
        spaceAfter=16,
    )
    section_heading_style = ParagraphStyle(
        'SectionHeading',
        fontName='Times-Bold',
        fontSize=18,
        textColor=colors.HexColor("#1C77C3"),
        alignment=0,
        spaceBefore=18,
        spaceAfter=10,
    )
    times_normal_style = ParagraphStyle(
        'TimesNormal',
        fontName='Times-Roman',
        fontSize=12,
    )
    summary_center_style = ParagraphStyle(
        'SummaryCenter',
        fontName='Times-Bold',
        fontSize=13,
        alignment=1,
        spaceBefore=16,
        spaceAfter=10,
    )

    # --- Header Information ---
    elements.append(Paragraph("MindMate Mental Wellness Report", colored_title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Date:</b> {now}", times_normal_style))
    elements.append(Spacer(1, 3))
    elements.append(Paragraph(f"<b>Language:</b> {st.session_state.language}", times_normal_style))
    elements.append(Spacer(1, 3))
    elements.append(Paragraph(f"<b>Messages Exchanged:</b> {len(st.session_state.messages)}", times_normal_style))
    elements.append(Spacer(1, 12))

    # --- Charts + Summary ---
    if st.session_state.chat_history:
        # Emotion stats for bar chart
        emotions = [c["emotion"] for c in st.session_state.chat_history]
        counts = Counter(emotions)
        emotion_labels = list(counts.keys())
        frequencies = [counts[emotion] for emotion in emotion_labels]
        plt.figure(figsize=(5.5,4))
        plt.bar(emotion_labels, frequencies, color="#00A313")
        plt.title("Emotion Distribution")
        plt.xlabel("Emotion")
        plt.ylabel("Frequency")
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        # Stress stats for pie chart
        stress_levels = [c.get("stress", "low") for c in st.session_state.chat_history]
        stress_counts = Counter(stress_levels)
        stress_labels = list(stress_counts.keys())
        stress_sizes = [stress_counts[sl] for sl in stress_labels]
        plt.figure(figsize=(4,4))
        plt.pie(stress_sizes, labels=stress_labels, autopct='%1.1f%%', colors=["#1C77C3", "#FFD166", "#EF476F"])
        plt.title("Stress Levels")
        plt.tight_layout()
        buf_pie = BytesIO()
        plt.savefig(buf_pie, format='png')
        buf_pie.seek(0)
        plt.close()

        # Combine charts side by side
        emotion_chart_img = Image(buf, width=300, height=210)
        stress_pie_img = Image(buf_pie, width=220, height=220)
        chart_table = Table([[emotion_chart_img, stress_pie_img]], colWidths=[320, 240], rowHeights=[220])
        chart_table.setStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')])
        elements.append(chart_table)

        # Dominant Emotion and levels (summary centered beneath both charts)
        dominant_emotion = max(counts, key=counts.get) if counts else "N/A"
        stress_counter = Counter(stress_levels)
        urgency_levels = [c.get("urgency", "low") for c in st.session_state.chat_history]
        urgency_counter = Counter(urgency_levels)
        overall_stress = max(stress_counter, key=stress_counter.get) if stress_counter else "N/A"
        overall_urgency = max(urgency_counter, key=urgency_counter.get) if urgency_counter else "N/A"
        summary_text = (
            f"<b>Dominant Emotion Detected:</b> {dominant_emotion.capitalize()}<br/>"
            f"<b>Overall Stress Level:</b> {overall_stress.capitalize()}<br/>"
            f"<b>Urgency Level:</b> {overall_urgency.capitalize()}"
        )
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(summary_text, summary_center_style))

    # --- Tips and Crisis, side by side ---
    # Prepare tips and crisis lists as Paragraphs (so each item is a Paragraph)
    tips_paragraphs = [Paragraph("<b>Personalized Tips</b>", section_heading_style)]
    tips_paragraphs.append(Spacer(1, 8))
    emotion_key = getattr(st.session_state, "current_emotion_for_tips", "neutral")
    tips = TIPS.get(emotion_key, ["Take care of yourself ",
                                  "Engage in activities you enjoy ",
                                  "Reach out to loved ones",
                                  "Practice mindfulness or relaxation techniques "])
    for tip in tips:
        tips_paragraphs.append(Paragraph(f"• {tip}", times_normal_style))
        tips_paragraphs.append(Spacer(1, 3))

    crisis = [
        "India: AASRA Helpline - 91-9820466726",
        "U.S.: Lifeline - 988",
        "UK: Samaritans - 116 123"
    ]
    crisis_paragraphs = [Paragraph("<b>Crisis Support</b>", section_heading_style)]
    crisis_paragraphs.append(Spacer(1, 8))
    for c in crisis:
        crisis_paragraphs.append(Paragraph(f"• {c}", times_normal_style))
        crisis_paragraphs.append(Spacer(1, 3))

    # Use a Table with two columns: tips and crisis
    side_by_side_table = Table([[tips_paragraphs, crisis_paragraphs]],
                              colWidths=[240, 240])
    side_by_side_table.setStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 10),
    ])
    elements.append(Spacer(1, 12))
    elements.append(side_by_side_table)
    
    # --- Build and save PDF ---
    doc.build(elements, canvasmaker=FooterCanvas)
    return filename



# --- Download button ---
st.markdown("---")
if st.button("📄 Generate My Session Report"):
    pdf_path = generate_mindmate_report()
    with open(pdf_path, "rb") as f:
        st.download_button(
            "⬇️ Download MindMate Report (PDF)",
            data=f,
            file_name="MindMate_Report.pdf",
            mime="application/pdf"
        )