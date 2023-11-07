import gradio as gr
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
import numpy as np
import os
import logging
import re

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Utility function for saving images with timestamp
def save_image_with_timestamp(output_image):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = f"output/{timestamp}.png"
        output_image.save(output_path, "PNG")
        return output_path
    except Exception as e:
        logging.error(f"Failed to save image with timestamp: {e}")
        return None

# Class for resource management
class ResourceLoader:
    @staticmethod
    def load_vintage_polaroid():
        """Load the vintage polaroid image."""
        try:
            return Image.open("resources/template.jpg")
        except Exception as e:
            logging.error(f"Resource loading failed: {e}")
            return None

    @staticmethod
    def load_gallery_images():
        """Load all images from the output directory."""
        return [
            os.path.join(root, file)
            for root, _, files in os.walk("output")
            for file in files
            if file.lower().endswith((".png", ".jpg", ".jpeg"))
        ]


# Class for image processing functionalities
class ImageProcessor:
    @staticmethod
    def add_mirrored_blur(img, dx, dy):
        """Add mirrored blur to the image edges."""
        try:
            if dx <= 0 or dy <= 0:
                return None, None, None, None
            # Mirror and blur each edge
            left = img.crop((0, 0, dx, img.height)).transpose(Image.FLIP_LEFT_RIGHT).filter(ImageFilter.GaussianBlur(20))
            right = img.crop((img.width - dx, 0, img.width, img.height)).transpose(Image.FLIP_LEFT_RIGHT).filter(ImageFilter.GaussianBlur(20))
            top = img.crop((0, 0, img.width, dy)).transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(20))
            bottom = img.crop((0, img.height - dy, img.width, img.height)).transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(20))
            return left, right, top, bottom
        except Exception as e:
            logging.error(f"Failed to add mirrored blur: {e}")
            return None, None, None, None

    @staticmethod
    def overlay_images(background, overlay, margin=161, bottom_margin=605, top_margin=161):
        """Overlay an image on a background image with margins."""
        try:
            background = background.convert("RGBA")
            overlay = overlay.convert("RGBA")
            # Calculate dimensions
            input_aspect_ratio = overlay.width / overlay.height
            target_width = background.width - 2 * margin
            target_height = background.height - bottom_margin - top_margin
            new_aspect_ratio = target_width / target_height
            new_width, new_height = (
                (target_width, int(target_width / input_aspect_ratio))
                if input_aspect_ratio > new_aspect_ratio
                else (int(target_height * input_aspect_ratio), target_height)
            )
            overlay = overlay.resize((new_width, new_height), Image.LANCZOS)
            # Calculate position offsets
            dx = (target_width - new_width) // 2
            dy = (target_height - new_height) // 2
            img_with_fill = Image.new("RGBA", (target_width, target_height))
            # Add mirrored blur if required
            if dx > 0 or dy > 0:
                left, right, top, bottom = ImageProcessor.add_mirrored_blur(overlay, dx, dy)
                if all([left, right, top, bottom]):
                    img_with_fill.paste(top, (dx, 0))
                    img_with_fill.paste(bottom, (dx, target_height - dy))
                    img_with_fill.paste(left, (0, dy))
                    img_with_fill.paste(right, (target_width - dx, dy))
            img_with_fill.paste(overlay, (dx, dy))
            overlay = img_with_fill
            background.paste(overlay, (margin, top_margin), overlay)
            return background
        except Exception as e:
            logging.error(f"Failed to overlay images: {e}")
            return None

    @staticmethod
    def add_text_to_image(img, text, font_size):
        """Add text to an image."""
        try:
            try:
                custom_font = ImageFont.truetype("resources/Font-6.ttf", size=200, encoding="unic")
            except Exception as font_error:
                logging.error(f"Failed to load custom font: {font_error}")
                # Handle the error by using a default font or providing an error message
                custom_font = ImageFont.load_default()  # Use a default font as a fallback

            draw = ImageDraw.Draw(img)
            max_width = img.width - 40
            lines = []
            words = text.split()
            while words:
                line = ""
                while words and custom_font.getlength(line + words[0]) <= max_width:
                    line += words.pop(0) + " "
                lines.append(line)
            y_text = img.height - len(lines) * font_size - 20
            for line in lines:
                width = draw.textlength(line, font=custom_font)
                position = ((img.width - width) // 2, y_text)
                draw.text(position, line, "black", font=custom_font)
                y_text += font_size
            return img
        except Exception as e:
            logging.error(f"Failed to add text: {e}", exc_info = e)
            return None

# Utility function for saving individual polaroids with text and timestamp in the filename
def save_individual_polaroid(output_image, text):
    try:
        # Ensure polaroid directory exists
        polaroid_dir = "output/polaroid"
        os.makedirs(polaroid_dir, exist_ok=True)

        # Sanitize the text to remove characters that are invalid in filenames
        sanitized_text = re.sub(r'[^\w\-_\. ]', '_', text)

        # Append the current date to the sanitized text
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{sanitized_text}_{date_str}.png"

        # Save the polaroid with the new filename
        polaroid_path = os.path.join(polaroid_dir, filename)
        output_image.save(polaroid_path, "PNG")
        logging.info(f"Saved polaroid to {polaroid_path}")
        return polaroid_path
    except Exception as e:
        logging.error(f"Failed to save individual polaroid: {e}")
        return None

# Class for Gradio interface setup
class GrInterface:
    TEMPLATE_WIDTH, TEMPLATE_HEIGHT = 1235, 1500
    CANVAS_WIDTH, CANVAS_HEIGHT = 2480, 3506

    @staticmethod
    def setup(image_data_list, font_size):
        """Create the Gradio interface."""
        try:
            image_data_list = [(img, txt) for img, txt in image_data_list if img is not None]
            num_images = len(image_data_list)
            canvas = Image.new('RGB', (GrInterface.CANVAS_WIDTH, GrInterface.CANVAS_HEIGHT), 'white')
            positions = [
                (0, 0),
                (GrInterface.CANVAS_WIDTH - GrInterface.TEMPLATE_WIDTH, 0),
                (0, GrInterface.CANVAS_HEIGHT - GrInterface.TEMPLATE_HEIGHT),
                (GrInterface.CANVAS_WIDTH - GrInterface.TEMPLATE_WIDTH, GrInterface.CANVAS_HEIGHT - GrInterface.TEMPLATE_HEIGHT)
            ]
            for i in range(num_images):
                input_img, text = image_data_list[i]
                if isinstance(input_img, np.ndarray):
                    input_img = Image.fromarray(input_img.astype('uint8'))
                overlayed_img = ImageProcessor.overlay_images(vintage_polaroid, input_img)
                if overlayed_img:
                    overlayed_img = overlayed_img.resize((GrInterface.TEMPLATE_WIDTH, GrInterface.TEMPLATE_HEIGHT), Image.LANCZOS)
                final_img = ImageProcessor.add_text_to_image(overlayed_img, text, int(font_size))
                if final_img:
                    # Save the individual polaroid
                    polaroid_path = save_individual_polaroid(final_img, text)
                    # Resize and paste the saved polaroid image onto the A4 canvas
                    if polaroid_path:
                        final_img = Image.open(polaroid_path).resize((GrInterface.TEMPLATE_WIDTH, GrInterface.TEMPLATE_HEIGHT), Image.LANCZOS)
                        canvas.paste(final_img, positions[i])

            # Return the canvas after the loop has finished
            return canvas
        except Exception as e:
            logging.error(f"Failed in GrInterface setup: {e}")
            return None
            


# Load resources
vintage_polaroid = ResourceLoader.load_vintage_polaroid()

# Define a global variable for the gallery images
global_gallery_images = ResourceLoader.load_gallery_images()

# Main execution
if __name__ == "__main__":
    gallery_images = ResourceLoader.load_gallery_images()
    input1 = gr.Image(label="Image 1")
    input2 = gr.Textbox(label="Text 1", value="Tekst 1")
    input3 = gr.Image(label="Image 2")
    input4 = gr.Textbox(label="Text 2", value="Tekst 2")
    input5 = gr.Image(label="Image 3")
    input6 = gr.Textbox(label="Text 3", value="Tekst 3")
    input7 = gr.Image(label="Image 4")
    input8 = gr.Textbox(label="Text 4", value="Tekst 4")
    font_size_input = gr.Number(label="Font Size", value=200)

    with gr.Blocks() as app_blocks:
        with gr.Tab("Generate"):
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
                b1.click(
                    lambda img1, txt1, img2, txt2, img3, txt3, img4, txt4, font_size: save_image_with_timestamp(
                        GrInterface.setup(
                            [(img1, txt1), (img2, txt2), (img3, txt3), (img4, txt4)],
                            font_size,
                        )
                    ),
                    inputs=[input1, input2, input3, input4, input5, input6, input7, input8, font_size_input],
                    outputs=output,
                )
        with gr.Tab("Image Browser"):
            # Initialize the gallery with the global variable
            gallery = gr.Gallery(label="Image Gallery", value=global_gallery_images, columns=4, allow_preview=True)
            refresh_button = gr.Button("Refresh")

            # Define the function that will be called when the refresh button is pressed
            def refresh_gallery():
                # Load new gallery images
                updated_gallery_images = ResourceLoader.load_gallery_images()
                # Return the new list of images to update the gallery
                return updated_gallery_images

            # Connect the 'refresh_gallery' function to the refresh button click event
            refresh_button.click(refresh_gallery, inputs=[], outputs=[gallery])

    app_blocks.launch(server_name='0.0.0.0', share=True)