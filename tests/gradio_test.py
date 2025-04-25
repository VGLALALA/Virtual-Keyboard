import gradio as gr

def greet(name):
    return f"Hello, {name}!"

iface = gr.Interface(
    fn=greet,
    inputs=gr.Textbox(label="Enter your name"),
    outputs=gr.Textbox(label="Greeting"),
    title="Greeting App",
    description="A simple app to greet the user.",
    theme=gr.themes.Soft()
)

# Customize the theme with a different color
iface.launch()
