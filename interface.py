import gradio as gr

# Stepwise UI state
TIPS = {
    "Happy 😊": [
        "Keep spreading your positivity",
        "Write down 3 things you’re grateful for",
        "Call someone and share your happiness"
    ],
    "Sad 😢": [
        "Have a good cry. It's a release, not a weakness",
        "Take a deep breath and write your thoughts",
        "Listen to calming music"
    ],
    "Stressed 😣": [
        "Try 5 minutes of deep breathing",
        "Go for a short walk",
        "You’re doing your best, one step at a time"
    ],
    "Angry 😠": [
        "Squeeze a stress ball or your fists to release the tension.",
        "Do some stretches or punch a pillow",
        "Channel your energy into journaling"
    ],
    "Tired 😴": [
        "Drink water",
        "Stretch or close your eyes for 2 minutes",
        "Take a break — you deserve rest"
    ]
}

custom_css = """
body {
  margin: 0; padding: 0;
  background: linear-gradient(135deg, #b3e5fc, #d1c4e9) !important;
  font-family: 'Poppins', sans-serif;
  color: #222;
  min-height: 100vh !important;
}
.container-mindmate {
  text-align: center;
  background: rgba(255,255,255,0.92);
  border-radius: 25px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.10);
  padding: 40px 60px;
  width: 90%;
  max-width: 650px;
  margin: 40px auto;
  animation: fadeIn 1.15s ease;
}
@keyframes fadeIn {
  from {opacity: 0; transform: translateY(20px);}
  to {opacity: 1; transform: translateY(0);}
}
.feeling-card {
  background: white;
  border-radius: 20px;
  padding: 18px 26px;
  font-size: 24px;
  cursor: pointer;
  margin: 10px 12px 8px 0;
  box-shadow: 0 5px 15px rgba(0,0,0,0.12);
  transition: 0.3s;
  display: inline-block;
  border: none;
}
.feeling-card:hover, .feeling-card.selected {
  background: #f3e5f5 !important;
  transform: translateY(-5px);
}
#step1 input, #step1 textarea {
  padding: 15px; border-radius: 12px;
  border: 1px solid #ccc; font-size: 18px;
  width: 70%;
  margin-top: 10px;
}
.gr-button {
  background-color: #6a1b9a !important;
  color: white !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 15px 35px !important;
  font-size: 18px !important;
  cursor: pointer !important;
  margin-top: 25px !important;
  transition: 0.3s;
}
.gr-button:hover {
  background-color: #8e24aa !important;
}
.back-btn {
  background-color: #ccc !important;
  color: #222 !important;
  margin-top: 15px !important;
  margin-right: 10px;
}
.back-btn:hover {
  background-color: #b0b0b0 !important;
}
.tips-list {
  margin-top: 20px; font-size: 18px; color: #333;
}
"""

with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    # Track the step, name, feeling in State
    gr.State("")
    gr.State("")
    gr.State(1)

    with gr.Column(elem_id="step1", visible=True, variant="panel", elem_classes=["container-mindmate"]) as step1_col:
        gr.HTML("<h1>Welcome to MindMate</h1>")

        gr.Markdown("<p style='font-size:20px;'>Let's begin, what's your name?</p>")
        name = gr.Textbox(label="", placeholder="Enter your name...", interactive=True)
        next1 = gr.Button("Next ➜")
        warn1 = gr.Markdown("", visible=False)

    with gr.Column(elem_id="step2", visible=False, variant="panel", elem_classes=["container-mindmate"]) as step2_col:
        user_name = gr.Markdown("", elem_id="userName")
        gr.Markdown("<p style='font-size:20px;'>How are you feeling today?</p>")
        feelings_row = gr.Row(equal_height=True)
        with feelings_row:
            feeling_choices = [
                "Happy 😊", "Sad 😢", "Stressed 😣", "Angry 😠", "Tired 😴"
            ]
            feeling_btns = [gr.Button(choice, elem_id=f"feeling-{i}", elem_classes=["feeling-card"]) for i, choice in enumerate(feeling_choices)]
        back2 = gr.Button("← Go Back", elem_classes=["back-btn"])

    with gr.Column(elem_id="step3", visible=False, variant="panel", elem_classes=["container-mindmate"]) as step3_col:
        tips_header = gr.Markdown("")
        tips_list = gr.Markdown("", elem_id="tipsList", elem_classes=["tips-list"])
        row3 = gr.Row()
        with row3:
            back3 = gr.Button("← Go Back", elem_classes=["back-btn"])
            chat_btn = gr.Button("Start Chatting 💬")

    # --- EVENTS & LOGIC ---
    def goto_step2(name_val):
        if not name_val or name_val.strip() == "":
            return gr.update(visible=True, value=":warning: Please enter your name 💬"), gr.update(visible=True, value=name_val)
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), f"<h1>Hi {name_val}!</h1>"
    next1.click(
        goto_step2,
        inputs=[name],
        outputs=[warn1, step1_col, step2_col, step3_col, user_name]
    )

    def goto_step3(feeling, name_val):
        tip_lines = TIPS[feeling]
        tips_html = "".join([f"<p>👉 {tip}</p>" for tip in tip_lines])
        return (
            gr.update(visible=False),  # step1
            gr.update(visible=False),  # step2
            gr.update(visible=True),   # step3
            f"<h1>Some tips for you, {name_val}</h1>",
            tips_html,
        )
    for i, btn in enumerate(feeling_btns):
        btn.click(
            goto_step3,
            inputs=[gr.State(feeling_choices[i]), name],
            outputs=[step1_col, step2_col, step3_col, tips_header, tips_list]
        )

    def back_to_1():
        return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(value=""), gr.update(value="")
    back2.click(back_to_1, outputs=[step1_col, step2_col, step3_col, name, user_name])

    def back_to_2(name_val):
        return (
            gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), f"<h1>Hi {name_val}!</h1>", "", ""
        )
    back3.click(back_to_2, inputs=[name], outputs=[step1_col, step2_col, step3_col, user_name, tips_header, tips_list])

    def open_chat():
        import webbrowser
        webbrowser.open("http://localhost:8501")
        return
    chat_btn.click(open_chat, outputs=[])

demo.launch()
