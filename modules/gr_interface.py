import gradio as gr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from .image_processing import overlay_images, add_text_to_image

# Initialize A4 dimensions
A4_WIDTH, A4_HEIGHT = 2480, 3508

# Gradio interface setup
def gr_interface(image_data_list, font_size, vintage_polaroid):
    try:
        # Filter out None values from the list
        image_data_list = [(img, txt) for img, txt in image_data_list if img is not None]
        num_images = len(image_data_list)

        # Create an empty white A4 canvas
        a4_canvas = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), 'white')

        # Coordinates for placing images in 4 corners
        positions = [(0, 0), (A4_WIDTH//2, 0), (0, A4_HEIGHT//2), (A4_WIDTH//2, A4_HEIGHT//2)]

        for i in range(num_images):
            input_img, text = image_data_list[i]
            if isinstance(input_img, np.ndarray):
                input_img = Image.fromarray(input_img.astype('uint8'))
            overlayed_img = overlay_images(vintage_polaroid, input_img)
            if overlayed_img:
                overlayed_img = overlayed_img.resize((A4_WIDTH//2, A4_HEIGHT//2), Image.LANCZOS)
                final_img = add_text_to_image(overlayed_img, text, int(font_size))
                if final_img:
                    a4_canvas.paste(final_img, positions[i])

        return a4_canvas
    except Exception as e:
        print(f"Failed in Gradio interface: {e}")
        return None