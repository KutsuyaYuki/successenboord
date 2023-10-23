from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import gradio as gr

# Initialize globals
vintage_polaroid = None

# Load resources function
def load_resources():
    global vintage_polaroid
    try:
        vintage_polaroid = Image.open("images/template.jpg")
    except Exception as e:
        print(f"Resource loading failed: {e}")

# Function to add mirrored blur
def add_mirrored_blur(img, dx, dy):
    try:
        if dx <= 0 or dy <= 0:
            return None, None, None, None
        left = img.crop((0, 0, dx, img.height)).transpose(Image.FLIP_LEFT_RIGHT)
        right = img.crop((img.width - dx, 0, img.width, img.height)).transpose(Image.FLIP_LEFT_RIGHT)
        top = img.crop((0, 0, img.width, dy)).transpose(Image.FLIP_TOP_BOTTOM)
        bottom = img.crop((0, img.height - dy, img.width, img.height)).transpose(Image.FLIP_TOP_BOTTOM)
        
        left = left.filter(ImageFilter.GaussianBlur(20))
        right = right.filter(ImageFilter.GaussianBlur(20))
        top = top.filter(ImageFilter.GaussianBlur(20))
        bottom = bottom.filter(ImageFilter.GaussianBlur(20))

        return left, right, top, bottom
    except Exception as e:
        print(f"Failed to add mirrored blur: {e}")
        return None, None, None, None

# Function to overlay images
def overlay_images(background, overlay, margin=161, bottom_margin=605, top_margin=161):
    try:
        background = background.convert("RGBA")
        overlay = overlay.convert("RGBA")

        input_aspect_ratio = overlay.width / overlay.height
        target_width = background.width - 2 * margin
        target_height = background.height - bottom_margin - top_margin
        new_aspect_ratio = target_width / target_height

        if input_aspect_ratio > new_aspect_ratio:
            new_width = target_width
            new_height = int(new_width / input_aspect_ratio)
        else:
            new_height = target_height
            new_width = int(new_height * input_aspect_ratio)

        overlay = overlay.resize((new_width, new_height), Image.LANCZOS)
        dx = (target_width - new_width) // 2
        dy = (target_height - new_height) // 2

        img_with_fill = Image.new('RGBA', (target_width, target_height))
        if dx > 0 or dy > 0:
            left, right, top, bottom = add_mirrored_blur(overlay, dx, dy)
            if left and right and top and bottom:
                img_with_fill.paste(top, (dx, 0))
                img_with_fill.paste(bottom, (dx, target_height - dy))
                img_with_fill.paste(left, (0, dy))
                img_with_fill.paste(right, (target_width - dx, dy))
        img_with_fill.paste(overlay, (dx, dy))
        overlay = img_with_fill

        background.paste(overlay, (margin, top_margin), overlay)
        return background
    except Exception as e:
        print(f"Failed to overlay images: {e}")
        return None
    
    # Function to add text to image
def add_text_to_image(img, text, font_size):
    try:
        # Initialize font here
        custom_font = ImageFont.truetype("fonts/Font-6.ttf", font_size)
        draw = ImageDraw.Draw(img)

        # Define maximum width for text
        max_width = img.width - 40  # 20 pixels padding on each side
        lines = []
        words = text.split()
        while words:
            line = ''
            while words and custom_font.getsize(line + words[0])[0] <= max_width:
                line += (words.pop(0) + ' ')
            lines.append(line)

        # Starting position
        y_text = img.height - len(lines) * font_size - 20  # 20 pixels padding from bottom

        # Draw text line by line
        for line in lines:
            width, height = draw.textsize(line, font=custom_font)
            # Draw text
            position = ((img.width - width) // 2, y_text)
            draw.text(position, line, "black", font=custom_font)
            y_text += font_size

        return img
    except Exception as e:
        print(f"Failed to add text: {e}")
        return None


# Gradio interface setup
def gr_interface(input_img, text, font_size):
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

# Create font previews
def create_font_previews(sample_text="Sample Text", font_files=["fonts/Font-6.ttf"]):
    previews = {}
    for font_file in font_files:
        try:
            img = Image.new('RGB', (300, 100), color='white')
            custom_font = ImageFont.truetype(font_file, 50)
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), sample_text, font=custom_font, fill="black")
            previews[font_file] = img
        except Exception as e:
            print(f"Failed to create font preview for {font_file}: {e}")
    return previews

# Main execution
if __name__ == "__main__":
    load_resources()
    iface = gr.Interface(
        fn=gr_interface,
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