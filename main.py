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
        fn=lambda img1, txt1, img2, txt2, img3, txt3, img4, txt4, font_size: 
            gr_interface(
                [(img1, txt1), (img2, txt2), (img3, txt3), (img4, txt4)], 
                font_size, 
                vintage_polaroid
            ),
        inputs=[
            gr.Image(label="Image 1", optional=True),
            gr.Textbox(label="Text 1", value="Text 1"),
            gr.Image(label="Image 2", optional=True),
            gr.Textbox(label="Text 2", value="Text 2"),
            gr.Image(label="Image 3", optional=True),
            gr.Textbox(label="Text 3", value="Text 3"),
            gr.Image(label="Image 4", optional=True),
            gr.Textbox(label="Text 4", value="Text 4"),
            gr.Textbox(label="Font Size", value="200")
        ],
        outputs=gr.Image(plot=True),
        live=False,
        capture_session=True,
        share=True
    )
    iface.launch()
