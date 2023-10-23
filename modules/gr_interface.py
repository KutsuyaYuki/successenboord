import gradio as gr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from .image_processing import overlay_images, add_text_to_image
import os
from datetime import datetime

# Initialize new template dimensions and total canvas size
TEMPLATE_WIDTH, TEMPLATE_HEIGHT = 1235, 1500
CANVAS_WIDTH, CANVAS_HEIGHT = 2480, 3506

# Gradio interface setup
def gr_interface(image_data_list, font_size, vintage_polaroid):
    try:
        # Filter out None values from the list
        image_data_list = [(img, txt) for img, txt in image_data_list if img is not None]
        num_images = len(image_data_list)

        # Create an empty white canvas with the dimensions you specified
        canvas = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), 'white')

        # Positions for placing images in 4 corners
        positions = [
            (0, 0),
            (CANVAS_WIDTH - TEMPLATE_WIDTH, 0),
            (0, CANVAS_HEIGHT - TEMPLATE_HEIGHT),
            (CANVAS_WIDTH - TEMPLATE_WIDTH, CANVAS_HEIGHT - TEMPLATE_HEIGHT)
        ]

        for i in range(num_images):
            input_img, text = image_data_list[i]
            if isinstance(input_img, np.ndarray):
                input_img = Image.fromarray(input_img.astype('uint8'))
            overlayed_img = overlay_images(vintage_polaroid, input_img)
            if overlayed_img:
                overlayed_img = overlayed_img.resize((TEMPLATE_WIDTH, TEMPLATE_HEIGHT), Image.LANCZOS)
                final_img = add_text_to_image(overlayed_img, text, int(font_size))
                if final_img:
                    canvas.paste(final_img, positions[i])

        # Get current date for folder naming
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Create 'input' folder if it doesn't exist
        if not os.path.exists('input'):
            os.mkdir('input')

        # Create a folder with the current date inside 'input'
        input_date_folder = os.path.join('input', current_date)
        if not os.path.exists(input_date_folder):
            os.mkdir(input_date_folder)

        # Save input images
        for i, (input_img, text) in enumerate(image_data_list):
            if isinstance(input_img, np.ndarray):
                input_img = Image.fromarray(input_img.astype('uint8'), 'RGB')
            input_img_path = os.path.join(input_date_folder, f"{text}.jpg")
            input_img.save(input_img_path)

        # Create 'output' folder if it doesn't exist
        if not os.path.exists('output'):
            os.mkdir('output')

        # Save the output image
        output_img_path = os.path.join('output', f"{current_date}.jpg")
        canvas.save(output_img_path)

        return canvas
    except Exception as e:
        print(f"Failed in Gradio interface: {e}")
        return None