import os
import time
import sys

# NumPy may crash in some macOS Accelerate setups during import-time checks.
# Avoid triggering that specific check while keeping runtime behavior intact.
if sys.platform == "darwin":
    sys.platform = "darwin-compat"

import gradio as gr
from generating_syllabus import generate_syllabus
from teaching_agent import teaching_agent

# import your OpenAI key (put in your .env file)
with open(".env", "r") as f:
    env_file = f.readlines()
envs_dict = {
    key.strip("'"): value.strip("\n")
    for key, value in [(i.split("=")) for i in env_file]
}
os.environ["OPENAI_API_KEY"] = envs_dict["OPENAI_API_KEY"]

with gr.Blocks() as demo:
    gr.Markdown("# Your AI Instructor")
    with gr.Tab("Input Your Information"):
        def _format_runtime_error(err: Exception) -> str:
            msg = str(err)
            if "You exceeded your current quota" in msg:
                return (
                    "OpenAI quota exceeded. Please add billing/credits to your "
                    "OpenAI account and try again."
                )
            return f"Runtime error: {msg}"

        def perform_task(input_text):
            # Perform the desired task based on the user input
            task = (
                "Generate a course syllabus to teach the topic: " + input_text
            )
            try:
                syllabus = generate_syllabus(input_text, task)
                teaching_agent.seed_agent(syllabus, task)
                return syllabus
            except Exception as err:
                return _format_runtime_error(err)

        text_input = gr.Textbox(
            label="State the name of topic you want to learn:"
        )
        text_output = gr.Textbox(label="Your syllabus will be showed here:")
        text_button = gr.Button("Build the Bot!!!")
        text_button.click(perform_task, text_input, text_output)
    with gr.Tab("AI Instructor"):
        #       inputbox = gr.Textbox("Input your text to build a Q&A Bot here.....")
        chatbot = gr.Chatbot()
        msg = gr.Textbox(label="What do you concern about?")
        clear = gr.Button("Clear")

        def user(user_message, history):
            teaching_agent.human_step(user_message)
            return "", history + [[user_message, None]]

        def bot(history):
            try:
                bot_message = teaching_agent.instructor_step()
            except Exception as err:
                history[-1][1] = _format_runtime_error(err)
                yield history
                return
            history[-1][1] = ""
            for character in bot_message:
                history[-1][1] += character
                time.sleep(0.05)
                yield history

        msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot, chatbot, chatbot
        )
        clear.click(lambda: None, None, chatbot, queue=False)
demo.queue().launch(debug=True, share=False)
