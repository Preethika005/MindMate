import streamlit as st
import time

st.set_page_config(page_title="Mindful Meditation Practice", page_icon="🧘")

st.markdown(
    """
    <style>
    /* Title style with smooth gradient */
    body {
        background-image: url('https://t4.ftcdn.net/jpg/04/29/98/53/360_F_429985307_Soobm8JrTAq3kOCM1GlJfq1J46COIvKb.jpg');
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center center;
    }
    h1 {
        font-weight: 700;
        background: linear-gradient(90deg, #4FACFE 0%, #00F2FE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 20px;
    }

    /* Paragraph and list text color */
    p, li {
        color: #4b4b4b;
        font-size: 16px;
        line-height: 1.6;
    }

    /* Ordered list number color */
    ol li {
        color: #31708f;
        font-weight: 600;
        margin-bottom: 8px;
    }

    /* Timer number */
    .timer-number {
        color: #00aaff;
        font-weight: 700;
    }

    /* Custom button styles */
    div.stButton > button {
        background: linear-gradient(90deg, #56ab2f, #a8e063);
        border: none;
        color: white;

        padding: 10px 23px;
        font-weight: 600;
        border-radius: 10px;
        transition: background 0.3s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #a8e063, #56ab2f);
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    "<h1 style='text-align: center;'>Mindful Meditation Practice</h1>",
    unsafe_allow_html=True
)
st.image("360_F_429985307_Soobm8JrTAq3kOCM1GlJfq1J46COIvKb.jpg", use_container_width=True)
with st.container():
    st.markdown(
        """
        <div style='background:rgba(255,255,255,0.75);padding:30px 40px;border-radius:20px;'>
        <p>Follow this guided meditation to cultivate mindfulness and inner peace:</p>
        <ul>
            <li>Find a quiet, comfortable place to sit or lie down</li>
            <li>Close your eyes and take a few deep breaths to settle in</li>
            <li>Bring your attention to your breath, noticing the inhales and exhales</li>
            <li>Scan your body from head to toe, releasing any tension</li>
            <li>Focus on the present moment, letting go of past and future thoughts</li>
            <li>If your mind wanders, gently bring it back to your breath</li>
            <li>Observe your thoughts without judgment, letting them pass like clouds</li>
            <li>Practice loving-kindness by sending positive thoughts to yourself and others</li>
            <li>Gradually expand your awareness to include sounds around you</li>
            <li>Slowly open your eyes and take a moment to reflect on your experience</li>
        </ul>
        <p>
        Start with 5-10 minutes daily and gradually increase the duration as you become more comfortable. Remember, consistency is key in developing a meditation practice.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Timer functionality ---
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "timer_paused" not in st.session_state:
    st.session_state.timer_paused = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "remaining_seconds" not in st.session_state:
    st.session_state.remaining_seconds = 300  # 5 minutes

def format_time(secs):
    mins = secs // 60
    s = secs % 60
    return f"{mins:02d}:{s:02d}"

st.markdown("<h2 style='text-align:center; margin-top:32px;'>Meditation Timer</h2>", unsafe_allow_html=True)
timer_placeholder = st.empty()

# --- Timer display ---
timer_placeholder.markdown(
    f"<div style='font-size:48px;text-align:center;color:#3DB2ED'>{format_time(st.session_state.remaining_seconds)}</div>",
    unsafe_allow_html=True
)

# --- Buttons ---
st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)  # Small vertical spacer
# col1, col2, col3 = st.columns(3)
# with col1:
#     if st.button("Start", key="start_button"):
#         if not st.session_state.timer_running:
#             st.session_state.timer_running = True
#             st.session_state.timer_paused = False
#             st.session_state.start_time = time.time()
# with col2:
#     if st.button("Pause", key="pause_button"):
#         if st.session_state.timer_running:
#             st.session_state.timer_paused = True
#             st.session_state.timer_running = False
#             elapsed = int(time.time() - st.session_state.start_time) if st.session_state.start_time else 0
#             st.session_state.remaining_seconds = max(0, st.session_state.remaining_seconds - elapsed)
# with col3:
#     if st.button("Reset", key="reset_button"):
#         st.session_state.timer_running = False
#         st.session_state.timer_paused = False
#         st.session_state.start_time = None
#         st.session_state.remaining_seconds = 300


# Center the buttons under timer using columns and spacers
col_spacer1, col_btn1, col_btn2, col_btn3, col_spacer2 = st.columns([2, 1, 1, 1, 2])

with col_btn1:
    start = st.button("Start", key="start_button")
with col_btn2:
    pause = st.button("Pause", key="pause_button")
with col_btn3:
    reset = st.button("Reset", key="reset_button")

# Button actions (immediately after button creation)
if start:
    if not st.session_state.timer_running:
        st.session_state.timer_running = True
        st.session_state.timer_paused = False
        st.session_state.start_time = time.time()

if pause:
    if st.session_state.timer_running:
        st.session_state.timer_paused = True
        st.session_state.timer_running = False
        elapsed = int(time.time() - st.session_state.start_time) if st.session_state.start_time else 0
        st.session_state.remaining_seconds = max(0, st.session_state.remaining_seconds - elapsed)

if reset:
    st.session_state.timer_running = False
    st.session_state.timer_paused = False
    st.session_state.start_time = None
    st.session_state.remaining_seconds = 300



# --- Timer Logic: runs only when timer is running ---
if st.session_state.timer_running and not st.session_state.timer_paused:
    # Count down
    if st.session_state.start_time:
        elapsed = int(time.time() - st.session_state.start_time)
        value = max(0, st.session_state.remaining_seconds - elapsed)
        timer_placeholder.markdown(
            f"<div style='font-size:48px;text-align:center;color:#3DB2ED'>{format_time(value)}</div>",
            unsafe_allow_html=True
        )
        if value > 0:
            time.sleep(1)
            st.rerun()
        else:
            st.session_state.timer_running = False
            st.session_state.timer_paused = False
            timer_placeholder.markdown(
                "<div style='font-size:48px;text-align:center;color:#3DB2ED'>00:00</div>",
                unsafe_allow_html=True
            )
            st.success("Meditation complete! Take a moment to enjoy your calmness.")
else:
    # Update so timer continues from where left off after pause
    timer_placeholder.markdown(
        f"<div class='timer-number' style='font-size:48px;text-align:center;'>{format_time(st.session_state.remaining_seconds)}</div>",
        unsafe_allow_html=True
    )