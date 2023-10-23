import gradio as gr
import numpy as np
from PIL import Image
from .image_processing import overlay_images, add_text_to_image

# Gradio interface setup
def gr_interface(input_img, text, font_size, vintage_polaroid):
    try:
        if isinstance(input_img, np.ndarray):
            input_img = Image.fromarray(input_img.astype('uint8'))
        overlayed_img = overlay_images(vintage_polaroid, input_img)
        if overlayed_img is None:
            return None
        final_img = add_text_to_image(overlayed_img, text, int(font_size))
        return final_img
    except Exception as e:
        print(f"Failed in Gradio interface: {e}")
        return None
