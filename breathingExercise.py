
# pages/1_Breathing_Exercise.py
import streamlit as st
import time
import base64
import os

st.set_page_config(page_title="Breathing Exercise", page_icon="🌬️", layout="wide")

# ========== CUSTOM STYLE ==========
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #e8f5e8 0%, #fff9c4 100%);
    color: #333;
}
# .stApp {
#     background: linear-gradient(135deg, #f0f9eb 0%, #fef7e0 100%);
#     color: #333;
# }
.back-to-home button {
    background: linear-gradient(135deg, #6a89cc 0%, #4a69bd 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 20px !important;
    padding: 10px 20px !important;
    font-size: 14px !important;
    font-weight: bold !important;
    transition: all 0.3s ease !important;
}

.back-to-home button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(106, 137, 204, 0.4) !important;
}
.main-container {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 25px;
    padding: 40px;
    margin: 20px 0;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    backdrop-filter: blur(10px);
}
.centered {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
}
.instruction-text {
    font-size: 32px;
    font-weight: bold;
    color: #2e7d32;
    text-align: center;
    margin-bottom: 10px;
}
.caption-text {
    font-size: 18px;
    color: #666;
    text-align: center;
    margin-top: 8px;
}
.cycle-counter {
    font-size: 20px;
    font-weight: bold;
    color: #764ba2;
    text-align: center;
    margin: 15px 0;
}
.stats-container {
    display: flex;
    justify-content: space-around;
    margin: 30px 0;
    padding: 20px;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 20px;
}
.stat-box {
    text-align: center;
    padding: 15px;
}
.stat-value {
    font-size: 28px;
    font-weight: bold;
    color: #667eea;
}
.stat-label {
    font-size: 14px;
    color: #666;
    margin-top: 5px;
}
.breathing-guide {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    padding: 25px;
    border-radius: 20px;
    margin: 25px 0;
    text-align: center;
}
.guide-step {
    display: inline-block;
    margin: 0 20px;
    text-align: center;
    vertical-align: top;
}
.guide-number {
    width: 50px;
    height: 50px;
    background: #667eea;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: bold;
    margin: 0 auto 10px;
}
button[data-baseweb="button"] {
    font-size: 18px !important;
    padding: 15px 30px !important;
    border-radius: 25px !important;
    border: none !important;
    font-weight: bold !important;
    transition: all 0.3s ease !important;
}
.start-btn {
    background: linear-gradient(135deg, #58cc71 0%, #2e7d32 100%) !important;
    color: white !important;
}
.start-btn:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 20px rgba(88, 204, 113, 0.3) !important;
}
.back-btn {
    background: linear-gradient(135deg, #f28b82 0%, #c62828 100%) !important;
    color: white !important;
}
.music-toggle {
    background: linear-gradient(135deg, #fdd835 0%, #f9a825 100%) !important;
    color: #333 !important;
}
.breathing-animation {
    position: relative;
    width: 300px;
    height: 300px;
    margin: 0 auto;
}
.pulse-circle {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    border-radius: 50%;
    background: conic-gradient(from 0deg, #667eea, #764ba2, #667eea);
    animation: pulse 4s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.7; }
    50% { transform: translate(-50%, -50%) scale(1.1); opacity: 1; }
}
.benefits-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin: 30px 0;
}
.benefit-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}
.benefit-card:hover {
    transform: translateY(-5px);
}
.benefit-icon {
    font-size: 40px;
    margin-bottom: 10px;
}
.back-to-home {
    position: absolute;
    top: 20px;
    right: 20px;
    z-index: 1000;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Hide the main Streamlit sidebar */
    [data-testid="stSidebar"], .css-1lcbmhc.e1fqkh3o3 {
        display: none !important;
    }
    /* Expand main content to full width */
    .block-container {
        padding-left: 2rem;
        padding-right: 2rem;
        margin-left: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)
# ===== MAIN CONTENT =====
with st.container():
    # st.markdown('<div class="main-container">', unsafe_allow_html=True)
    # # ===== Back to Home Button =====
    # st.markdown("""
    # <div class="back-to-home">
    # """, unsafe_allow_html=True)

    # col1, col2, col3 = st.columns([3, 1, 1])
    # with col3:
    #     if st.button("🏠 Back to Home", key="back_home"):
    #         st.switch_page("mindmate_ui.py")  # Replace with your home page filename

    # st.markdown("</div>", unsafe_allow_html=True)

    st.title("🌬️ Peaceful Breathing Exercise")
    st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <p style='font-size: 20px; color: #666;'>Follow the expanding circle and calm your mind with the proven 4-7-8 breathing technique</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== Breathing Guide =====
    st.markdown("""
    <div class="breathing-guide">
        <h3 style='text-align: center; color: #333; margin-bottom: 20px;'>🎯 How to Practice 4-7-8 Breathing</h3>
        <div class="guide-step">
            <div class="guide-number">1</div>
            <strong>Inhale</strong><br>4 seconds
        </div>
        <div class="guide-step">
            <div class="guide-number">2</div>
            <strong>Hold</strong><br>7 seconds
        </div>
        <div class="guide-step">
            <div class="guide-number">3</div>
            <strong>Exhale</strong><br>8 seconds
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== Benefits Grid =====
    st.markdown("""
    <div class="benefits-grid">
        <div class="benefit-card">
            <div class="benefit-icon">😌</div>
            <h4>Reduces Stress</h4>
            <p>Activates parasympathetic nervous system for relaxation</p>
        </div>
        <div class="benefit-card">
            <div class="benefit-icon">💤</div>
            <h4>Improves Sleep</h4>
            <p>Calms the mind and prepares body for restful sleep</p>
        </div>
        <div class="benefit-card">
            <div class="benefit-icon">🎯</div>
            <h4>Enhances Focus</h4>
            <p>Increases oxygen flow to brain for better concentration</p>
        </div>
        <div class="benefit-card">
            <div class="benefit-icon">❤️</div>
            <h4>Lowers Blood Pressure</h4>
            <p>Promotes cardiovascular health and relaxation</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    placeholder = st.empty()
    caption = st.empty()
    cycle_counter = st.empty()

    # ===== Stats Container =====
    stats_placeholder = st.empty()

    # ===== Optional Background Music =====
    music_file = "calm_music.mp3"
    if os.path.exists(music_file):
        with open(music_file, "rb") as f:
            music_data = f.read()
        music_base64 = base64.b64encode(music_data).decode()
        music_html = f"""
        <audio id="bg-music" autoplay loop>
            <source src="data:audio/mp3;base64,{music_base64}" type="audio/mp3">
        </audio>
        """
    else:
        music_html = ""

    # ===== Function: Breathing Animation =====
    def animate_breathing(cycles=3, inhale=4, hold=7, exhale=8):
        min_r, max_r = 30, 150
        total_time = cycles * (inhale + hold + exhale)
        start_time = time.time()
        
        # Update stats
        stats_placeholder.markdown(f"""
        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-value">{cycles}</div>
                <div class="stat-label">Total Cycles</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{total_time}s</div>
                <div class="stat-label">Total Time</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">4-7-8</div>
                <div class="stat-label">Breathing Pattern</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        for cycle in range(cycles):
            cycle_counter.markdown(f'<div class="cycle-counter">🔄 Cycle {cycle + 1} of {cycles}</div>', unsafe_allow_html=True)
            
            # --- INHALE ---
            frames = int(inhale * 12)
            for i in range(frames + 1):
                r = int(min_r + (max_r - min_r) * (i / frames))
                color = f"rgba(102, 126, 234, {0.6 + 0.3*i/frames})"
                svg = f"""
                <div class='centered'>
                <svg width="300" height="300">
                    <circle cx="150" cy="150" r="{r}" fill="{color}" stroke="#764ba2" stroke-width="3" />
                    <text x="150" y="155" font-size="32" text-anchor="middle" fill="#2e7d32" font-weight="bold">Inhale</text>
                </svg>
                </div>
                """
                placeholder.markdown(svg, unsafe_allow_html=True)
                caption.markdown(f"<div class='caption-text'>⏱️ Time left: {int(inhale - i * inhale / frames)}s</div>", unsafe_allow_html=True)
                time.sleep(inhale / frames)

            # --- HOLD ---
            svg = f"""
            <div class='centered'>
            <svg width="300" height="300">
                <circle cx="150" cy="150" r="{max_r}" fill="#764ba2" stroke="#667eea" stroke-width="3" />
                <text x="150" y="155" font-size="32" text-anchor="middle" fill="white" font-weight="bold">Hold</text>
            </svg>
            </div>
            """
            placeholder.markdown(svg, unsafe_allow_html=True)
            caption.markdown(f"<div class='caption-text'>⏸️ Hold for {hold} seconds</div>", unsafe_allow_html=True)
            time.sleep(hold)

            # --- EXHALE ---
            frames = int(exhale * 12)
            for i in range(frames + 1):
                r = int(max_r - (max_r - min_r) * (i / frames))
                color = f"rgba(118, 75, 162, {0.9 - 0.3*i/frames})"
                svg = f"""
                <div class='centered'>
                <svg width="300" height="300">
                    <circle cx="150" cy="150" r="{r}" fill="{color}" stroke="#667eea" stroke-width="3" />
                    <text x="150" y="155" font-size="32" text-anchor="middle" fill="#2e7d32" font-weight="bold">Exhale</text>
                </svg>
                </div>
                """
                placeholder.markdown(svg, unsafe_allow_html=True)
                caption.markdown(f"<div class='caption-text'>⏱️ Time left: {int(exhale - i * exhale / frames)}s</div>", unsafe_allow_html=True)
                time.sleep(exhale / frames)

        # End
        elapsed_time = int(time.time() - start_time)
        placeholder.markdown("""
        <div class='centered'>
            <div style='text-align: center;'>
                <h2 style='color: #2e7d32;'>✨ Session Complete! ✨</h2>
                <div style='font-size: 60px; margin: 20px 0;'>🎉</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        caption.markdown(f"""
        <div class='caption-text'>
            <strong>Well done! 🎊</strong><br>
            You completed {cycles} breathing cycles in {elapsed_time} seconds.<br>
            Take a moment to notice how calm you feel 💙
        </div>
        """, unsafe_allow_html=True)
        cycle_counter.markdown("", unsafe_allow_html=True)
        st.balloons()

    # ===== Buttons =====
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🧘 Start Breathing Session", key="start", use_container_width=True):
            st.markdown(music_html, unsafe_allow_html=True)
            animate_breathing(cycles=3)

    # Additional options
    col4, col5, col6 = st.columns([1, 1, 1])
    with col4:
        if st.button("🎵 Play Background Music", key="music"):
            st.markdown(music_html, unsafe_allow_html=True)
            st.success("Calming music started 🎶")
    
    with col6:
        if st.button("ℹ️ Breathing Tips", key="tips"):
            st.info("""
            **Pro Tips for Better Breathing:**
            - Sit comfortably with straight back
            - Place tongue behind front teeth
            - Breathe quietly through nose
            - Exhale completely through mouth
            - Practice 2x daily for best results
            """)

    st.markdown('</div>', unsafe_allow_html=True)

# ===== Footer =====
st.markdown("""
<div style='text-align: center; margin-top: 40px; color: blue;'>
    <p>💡 <em>Regular practice of 4-7-8 breathing can significantly reduce anxiety and improve sleep quality</em></p>
</div>
""", unsafe_allow_html=True)

# Back to chatbot (commented out as in original)
# with st.sidebar:
#     if st.button("⬅️ Back to Chatbot"):
#         st.switch_page("mindmate_ui.py")