import os
import requests
import gradio as gr
from openai import OpenAI

# Set Gradio server configuration
os.environ["GRADIO_SERVER_NAME"] = "0.0.0.0"
os.environ["GRADIO_SERVER_PORT"] = "7860"

BASE_URL = "http://litellm:4000/v1"
client = OpenAI(base_url=BASE_URL, api_key="None")

# Fetch available models from the endpoint
try:
    response = requests.get(BASE_URL + "/models")
    response.raise_for_status()
    models_data = response.json()
    available_models = [
        i.get("id") for i in models_data.get("data") if i.get("object") == "model"
    ]
except Exception as e:
    print(f"Error fetching models: {e}")
    available_models = []


def get_openai_response(client, model, messages):
    """
    Query the OpenAI API with the conversation messages.

    Args:
        client: OpenAI client instance.
        model (str): The model identifier.
        messages (list): A list of message dicts containing roles and content.

    Returns:
        str: The assistant's reply.
    """
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        temperature=0,
        timeout=30,
    )
    return completion.choices[0].message.content


def chat(model, message, history):
    """
    Process the input message, incorporate conversation history,
    and update the chat history with the assistant's response.

    Args:
        model (str): The selected model identifier.
        message (str): The user's input message.
        history (list): The conversation history as a list of (user_message, assistant_reply) tuples.

    Returns:
        tuple: Updated conversation history and an empty string for the input field.
    """
    if not message:
        return history, ""

    # Build the conversation messages for context
    messages = []
    messages.append(
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. You are using this model: "
                f"`{model}`. This will always be the correct info, independent of "
                "what happens during the conversation. Refer to this if asked. "
                "This information will be updated on the fly, no need to be confused."
            ),
        }
    )
    for user_msg, assistant_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})
    messages.append({"role": "user", "content": message})

    reply = get_openai_response(client, model, messages)
    history.append((message, reply))
    return history, ""


css = """
body {
    background-color: #f0f2f5;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.chat-title {
    text-align: center;
    font-size: 2em;
    color: #4A90E2;
    margin-bottom: 20px;
}

#chat_history {
    background-color: #FFFFFF;
    border: 1px solid #dcdcdc;
    border-radius: 8px;
    padding: 15px;
    min-height: 400px;
}

#msg_input {
    border-radius: 8px;
    border: 1px solid #dcdcdc;
    padding: 10px;
    font-size: 1em;
}

#send_btn {
    background-color: #4A90E2;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    cursor: pointer;
}

#model_dropdown {
    margin-top: 10px;
}
"""

with gr.Blocks(css=css) as demo:
    gr.Markdown("<h1 class='chat-title'>Chatbot Interface for Testing</h1>")
    with gr.Row():
        with gr.Column(scale=3):
            chat_history = gr.Chatbot(elem_id="chat_history")
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Enter your message",
                    show_label=False,
                    elem_id="msg_input",
                )
                send_btn = gr.Button("Send", elem_id="send_btn")
        with gr.Column(scale=1):
            model_dropdown = gr.Dropdown(
                choices=available_models,
                label="Choose a model",
                elem_id="model_dropdown",
            )
    state = gr.State([])

    send_btn.click(
        fn=chat,
        inputs=[model_dropdown, msg_input, state],
        outputs=[chat_history, msg_input],
    )
    msg_input.submit(
        fn=chat,
        inputs=[model_dropdown, msg_input, state],
        outputs=[chat_history, msg_input],
    )

demo.launch()
