import gradio as gr
from PIL import Image
from modules.image_processing import (
    add_text_to_image,
    overlay_images,
    add_mirrored_blur,
)
from modules.gr_interface import gr_interface
import os

# Initialize globals
vintage_polaroid = None

# Load resources function
def load_resources():
    global vintage_polaroid
    try:
        vintage_polaroid = Image.open("resources/template.jpg")
    except Exception as e:
        print(f"Resource loading failed: {e}")

# Define input components
input1 = gr.Image(label="Image 1")
input2 = gr.Textbox(label="Text 1", value="Tekst 1")
# Define additional input components
input3 = gr.Image(label="Image 2")
input4 = gr.Textbox(label="Text 2", value="Tekst 2")
input5 = gr.Image(label="Image 3")
input6 = gr.Textbox(label="Text 3", value="Tekst 3")
input7 = gr.Image(label="Image 4")
input8 = gr.Textbox(label="Text 4", value="Tekst 4")
font_size_input = gr.Number(label="Font Size", value=200)

# Main execution
if __name__ == "__main__":
    load_resources()

    with gr.Blocks() as app_blocks:
        with gr.Tab("Generate"):  # Create the "Generate" tab
            with gr.Row():
                with gr.Column():
                    input1.render()
                    input2.render()
                with gr.Column():
                    input3.render()
                    input4.render()
            with gr.Row():
                with gr.Column():
                    input5.render()
                    input6.render()
                with gr.Column():
                    input7.render()
                    input8.render()
            with gr.Row():
                font_size_input.render()
            with gr.Row():
                with gr.Column(scale=2):
                    b1 = gr.Button("Go")
                    output = gr.Image()

                b1.click(lambda img1, txt1, img2, txt2, img3, txt3, img4, txt4, font_size: gr_interface(
                    [(img1, txt1), (img2, txt2), (img3, txt3), (img4, txt4)],
                    font_size,
                    vintage_polaroid,
                ), inputs=[input1, input2, input3, input4, input5, input6, input7, input8, font_size_input], outputs=output)

        with gr.Tab("Image Browser"):  # Create the "Image Browser" tab
            with gr.Row():
                with gr.Column():
                    # textbox
                    output = gr.Image()             
    app_blocks.launch()
