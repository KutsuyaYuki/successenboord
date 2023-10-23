import gradio as gr
from PIL import Image
from modules.image_processing import add_text_to_image, overlay_images, add_mirrored_blur
from modules.gr_interface import gr_interface

# Initialize globals
vintage_polaroid = None

# Load resources function
def load_resources():
    global vintage_polaroid
    try:
        vintage_polaroid = Image.open("resources/template.jpg")
    except Exception as e:
        print(f"Resource loading failed: {e}")

# Main execution
if __name__ == "__main__":
    load_resources()
    iface = gr.Interface(
        # Use lambda to include vintage_polaroid
        fn=lambda input_img, text, font_size: gr_interface(input_img, text, font_size, vintage_polaroid),
        inputs=[
            gr.Image(label="Input Image"),
            gr.Textbox(label="Text to Add", value="Meow!"),
            gr.Textbox(label="Font Size", value="200")
        ],
        outputs=gr.Image(plot=True),
        live=False,
        capture_session=True,
        share=True
    )
    iface.launch()
