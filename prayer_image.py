import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import textwrap
import os
import re
from datetime import datetime

def create_gradient_background(width, height):
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    X, Y = np.meshgrid(x, y)
    gradient = ((1 - (X + Y) / 2) * 0.6)
    rgb_array = np.zeros((height, width, 3))
    rgb_array[..., 0] = gradient * 180
    gradient_img = Image.fromarray(np.uint8(rgb_array))
    return gradient_img

def measure_text_height(text, font, max_width, draw, line_spacing_factor=0.1):
    lines = []
    current_line = []
    words = text.split()

    # Build lines word by word
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]
        if line_width <= max_width:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))

    total_height = 0
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])

    # Add a bit of spacing between lines
    line_spacing = int(font.size * line_spacing_factor)
    total_height = sum(line_heights) + line_spacing * (len(lines) - 1)
    return total_height, lines

def get_font_size_that_fits(text, max_width, max_height, font_path=None, max_size=300, min_size=10):
    temp_img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(temp_img)

    best_size = min_size
    low, high = min_size, max_size

    while low <= high:
        mid = (low + high) // 2
        try:
            if font_path:
                font = ImageFont.truetype(font_path, mid)
            else:
                try:
                    font = ImageFont.truetype("Arial Bold", mid)
                except:
                    font = ImageFont.truetype("Arial", mid)
        except:
            font = ImageFont.load_default()

        text_height, _ = measure_text_height(text, font, max_width, draw, 0.1)
        if text_height <= max_height:
            best_size = mid
            low = mid + 1
        else:
            high = mid - 1

    return best_size

def parse_prayer_number(text):
    match = re.search(r'(?i)\bprayer\s+(\d+)\b', text)
    if match:
        return match.group(1)
    return None

def parse_scripture_reference(text):
    pattern = r'[1-3]?\s?[A-Z][a-z]+\.\s?\d+:\d+(?:-\d+)?'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return None

def create_prayer_image(text, date_text="", output_filename="prayer.png", width=1920, height=1080):
    prayer_num = parse_prayer_number(text)
    if prayer_num:
        pattern_prayer = re.compile(r'(?i)\bprayer\s+' + re.escape(prayer_num) + r'\b')
        text = pattern_prayer.sub('', text, count=1).strip()

    scripture_ref = parse_scripture_reference(text)
    if scripture_ref:
        text = re.sub(re.escape(scripture_ref), '', text, count=1).strip()

    text = re.sub(r'^[;:]\s*', '', text)

    header_parts = []
    if prayer_num:
        header_parts.append(f"PRAYER {prayer_num}")
    if scripture_ref:
        header_parts.append(scripture_ref.upper())
    header_text = " | ".join(header_parts)

    img = create_gradient_background(width, height)
    draw = ImageDraw.Draw(img)

    margin_x = width * 0.04
    margin_y = height * 0.04
    max_width_area = width - 2 * margin_x
    max_height_area = height - 2 * margin_y

    title_font_size = 0
    if header_text:
        title_font_size = get_font_size_that_fits(
            header_text,
            max_width_area * 0.9,
            margin_y * 3,
            max_size=200
        )

    main_text = text.upper()

    main_font_size = get_font_size_that_fits(
        main_text,
        max_width_area * 0.9,
        max_height_area - (margin_y * 3) if header_text else max_height_area,
        max_size=1000
    )

    try:
        title_font = ImageFont.truetype("Arial Bold", title_font_size) if title_font_size > 0 else None
        main_font = ImageFont.truetype("Arial Bold", main_font_size)
    except:
        title_font = main_font = ImageFont.load_default()

    y_cursor = margin_y

    if header_text and title_font:
        bbox_title = draw.textbbox((0, 0), header_text, font=title_font)
        header_width = bbox_title[2] - bbox_title[0]
        x_header = (width - header_width) / 2

        for offset in range(1, 3):
            draw.text((x_header + offset, y_cursor + offset), header_text, font=title_font, fill=(0, 0, 0))
        draw.text((x_header, y_cursor), header_text, font=title_font, fill="white")
        y_cursor += (bbox_title[3] - bbox_title[1]) + (title_font_size * 0.2)

    temp_img = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    text_height, lines = measure_text_height(main_text, main_font, max_width_area, temp_draw, 0.1)

    remaining_height = height - y_cursor - margin_y
    y_cursor += max(0, (remaining_height - text_height) / 2)

    line_spacing = int(main_font.size * 0.1)

    for line in lines:
        bbox_line = draw.textbbox((0, 0), line, font=main_font)
        line_width = bbox_line[2] - bbox_line[0]
        x_line = (width - line_width) / 2

        for offset in range(1, 3):
            draw.text((x_line + offset, y_cursor + offset), line, font=main_font, fill=(0, 0, 0))
        draw.text((x_line, y_cursor), line, font=main_font, fill="white")

        y_cursor += (bbox_line[3] - bbox_line[1]) + line_spacing

    img.save(output_filename, "PNG")
    print(f"Image saved as {output_filename}")

class PrayerImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Prayer Image Generator")
        
        self.root.geometry("800x600")
        self.root.configure(padx=20, pady=20)
        
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        instructions = (
            "Enter your prayers or announcements below.\n"
            "Separate each new item with a line break."
        )
        ttk.Label(main_frame, text=instructions).pack(pady=(0, 5))
        
        self.text_input = scrolledtext.ScrolledText(main_frame, height=15, width=70, wrap=tk.WORD)
        self.text_input.pack(pady=(0, 20), fill=tk.BOTH, expand=True)
        
        generate_btn = ttk.Button(main_frame, text="Generate Images", command=self.generate_images)
        generate_btn.pack(pady=(0, 10))
        
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.pack()
        
        if not os.path.exists("generated_prayers"):
            os.makedirs("generated_prayers")
    
    def generate_images(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            self.status_label.config(text="Please enter some text first!")
            return
        
        prayers = [prayer.strip() for prayer in text.split('\n') if prayer.strip()]
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            successful_images = 0
            
            for i, prayer in enumerate(prayers, 1):
                output_filename = os.path.join(
                    "generated_prayers", 
                    f"prayer_{timestamp}_{i}.png"
                )
                create_prayer_image(prayer, output_filename=output_filename)
                successful_images += 1
            
            self.status_label.config(
                text=f"Created {successful_images} images in 'generated_prayers'!"
            )
            os.system(f"open {os.path.abspath('generated_prayers')}")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")

def main():
    root = tk.Tk()
    app = PrayerImageApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()