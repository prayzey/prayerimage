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
    try:
        # Get font metrics
        ascent, descent = font.getmetrics()
        line_height = ascent + descent
        print(f"Font metrics - size: {font.size}, ascent: {ascent}, descent: {descent}, line height: {line_height}")
        # Match Vercel's default font metrics ratio
        if isinstance(font, ImageFont.ImageFont):  # If using default font
            line_height = 13 * (font.size / 10)  # Scale based on Vercel's ratio
    except Exception as e:
        print(f"Error getting font metrics: {e}, using Vercel default metrics")
        line_height = 13 * (font.size / 10)

    # Use more horizontal space
    effective_max_width = max_width * 0.98  # Use 98% of available width
    
    lines = []
    current_line = []
    words = text.split()

    def split_long_word(word):
        # Special handling for email addresses and long words
        if '@' in word:
            # Split email at @ and . characters
            parts = []
            current = ''
            for char in word:
                if char in ['@', '.']:
                    if current:
                        parts.append(current)
                    parts.append(char)
                    current = ''
                else:
                    current += char
            if current:
                parts.append(current)
            return parts
        else:
            # For other long words, split at reasonable length
            max_chunk = 20  # Increased maximum characters per chunk
            return [word[i:i+max_chunk] for i in range(0, len(word), max_chunk)]

    # Build lines word by word, trying to maximize width usage
    for word in words:
        # Try adding the word to current line
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]
        
        if line_width <= effective_max_width:
            current_line.append(word)
        else:
            # Try to find optimal split point for maximum width usage
            if current_line:
                # Find the best split point that uses the most width
                best_width = 0
                best_split = len(current_line)
                test_words = current_line + [word]
                
                for i in range(1, len(test_words)):
                    test_line = " ".join(test_words[:i])
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    width = bbox[2] - bbox[0]
                    
                    if width <= effective_max_width and width > best_width:
                        best_width = width
                        best_split = i
                
                lines.append(" ".join(test_words[:best_split]))
                current_line = test_words[best_split:]
            else:
                # Handle single long word
                word_parts = split_long_word(word)
                current_part = ''
                
                for part in word_parts:
                    test_part = current_part + part if current_part else part
                    part_bbox = draw.textbbox((0, 0), test_part, font=font)
                    
                    if part_bbox[2] - part_bbox[0] <= effective_max_width:
                        current_part = test_part
                    else:
                        if current_part:
                            lines.append(current_part)
                        current_part = part
                
                if current_part:
                    current_line = [current_part]
    
    if current_line:
        lines.append(" ".join(current_line))

    # Use Vercel's exact metrics for height
    total_height = 280 * len(lines)  # Use Vercel's line height (280)
    return total_height, lines

def get_font_size_that_fits(text, max_width, max_height, font_path=None, max_size=300, min_size=150):
    # Use exact same font loading as Vercel
    import os
    font = None
    
    # Define font paths exactly as in Vercel
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_paths = [
        os.path.join(current_dir, 'api', 'fonts', 'ArialBold.ttf'),  # Local path matching Vercel
        '/var/task/api/fonts/ArialBold.ttf',  # Vercel path
    ]
    
    # Try loading our custom TTF first
    for path in font_paths:
        try:
            if os.path.isfile(path):
                print(f"Loading font from: {path}")
                font = ImageFont.truetype(path, size=min_size)
                break
        except Exception as e:
            print(f"Failed to load font {path}: {e}")
            continue
    
    # If custom font fails, use default
    if font is None:
        print("No custom fonts found, using default font")
        font = ImageFont.load_default()
    temp_img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(temp_img)

    # Use the full provided dimensions
    print(f"Using dimensions - width: {max_width}, height: {max_height}")

    best_size = min_size
    low, high = min_size, max_size

    while low <= high:
        mid = (low + high) // 2
        # Try loading fonts in order of preference
        font = None
        errors = []
        
        try:
            if font_path:
                try:
                    font = ImageFont.truetype(font_path, mid)
                except Exception as e:
                    errors.append(f"Could not load custom font: {e}")
            
            if not font:
                try:
                    font = ImageFont.truetype("Arial Bold", mid)
                except Exception as e:
                    errors.append(f"Could not load Arial Bold: {e}")
                    
                    try:
                        font = ImageFont.truetype("Arial", mid)
                    except Exception as e:
                        errors.append(f"Could not load Arial: {e}")
            
            if not font:
                print(f"Font loading errors: {'; '.join(errors)}")
                font = ImageFont.load_default()
                print("Using default font as fallback")
        except Exception as e:
            print(f"Unexpected error loading fonts: {e}")
            font = ImageFont.load_default()

        try:
            text_height, lines = measure_text_height(text, font, max_width, draw, 0.1)
            # Get font metrics for height calculation
            try:
                ascent, descent = font.getmetrics()
                line_height = ascent + descent
            except:
                line_height = font.size
            
            # Calculate actual height using line height
            line_spacing = 0.1  # Define line spacing factor
            actual_height = line_height * len(lines) * (1 + line_spacing)
            # Debug logging
            print(f"Trying font size {mid}: calculated height = {text_height}, actual height = {actual_height}, max height = {max_height}")
            print(f"Text lines at size {mid}: {lines}")
            text_height = actual_height  # Use the actual height calculation
        except Exception as e:
            print(f"Error measuring text: {e}")
            text_height = max_height + 1  # Force size reduction

        if text_height <= max_height:
            best_size = mid
            low = mid + 1
        else:
            high = mid - 1

    # Return the best size found
    print(f"Final font size selected: {best_size}")
    return best_size

def parse_prayer_number(text):
    match = re.search(r'(?i)\bprayer\s+(\d+)\b', text)
    if match:
        return match.group(1)
    return None

def parse_scripture_reference(text):
    # More comprehensive pattern to match various book abbreviations
    pattern = r'(?:[1-3]\s?)?[A-Z][a-z]*\.\s?\d+:\d+(?:-\d+)?'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return None

def split_long_text(text, max_chars=270, min_remaining_words=10):
    """Split text into multiple parts if it exceeds max_chars while keeping sentences and phrases intact.
    
    Args:
        text: The text to split
        max_chars: Maximum characters per part
        min_remaining_words: Minimum number of words required to create a new part
    """
    # If text is short enough, return as single part
    if len(text) <= max_chars:
        return [text]
    
    # First, identify scripture references
    scripture_ref = parse_scripture_reference(text)
    
    # Split text into sentences while preserving scripture references
    parts = []
    current_part = ""
    words = text.split()
    i = 0
    
    # If there's a scripture reference at the start, handle it first
    if scripture_ref and text.startswith(scripture_ref):
        current_part = scripture_ref
        i = len(scripture_ref.split())
    
    while i < len(words):
        word = words[i]
        test_part = current_part + (" " if current_part else "") + word
        
        # Calculate remaining words
        remaining_words = len(words) - i - 1
        
        # Normal word processing
        if len(test_part) <= max_chars:
            current_part = test_part
        else:
            if current_part:
                parts.append(current_part)
            current_part = word
            
        # If we're near the end, try to keep remaining words together
        if remaining_words <= min_remaining_words and i == len(words) - remaining_words - 1:
            remaining_text = " ".join(words[i+1:])
            test_full_part = current_part + (" " if current_part else "") + remaining_text
            if len(test_full_part) <= max_chars * 1.5:  # Allow up to 50% longer for final part
                current_part = test_full_part
                break
        
        # Check for sentence endings (but not in scripture references)
        if word.endswith(('.', '!', '?')) and (not scripture_ref or word not in scripture_ref):
            # Only split on sentence end if we have enough words remaining
            if remaining_words > min_remaining_words:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
        
        i += 1
    
    if current_part:  # Add any remaining text
        parts.append(current_part)
    
    return parts
    
    return parts

def add_logo(img, logo_path, target_width=100):  # Reduced from 150px to 100px for smaller logo
    try:
        # Open and convert logo to RGBA to preserve transparency
        logo = Image.open(logo_path).convert('RGBA')
        
        # Calculate height while maintaining aspect ratio
        aspect_ratio = logo.height / logo.width
        target_height = int(target_width * aspect_ratio)
        
        # Resize logo
        logo = logo.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Calculate position (top left with padding)
        padding = 20
        position = (padding, padding)
        
        # Create a new image with the same size as background for compositing
        logo_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        logo_layer.paste(logo, position, logo)
        
        # Composite the images
        return Image.alpha_composite(img.convert('RGBA'), logo_layer)
    except Exception as e:
        print(f"Error adding logo: {e}")
        return img

def create_prayer_image(text, date_text="", output_filename="prayer.png", width=1920, height=1080):
    # Use dimensions that work well for our environment
    width = 1920
    height = 1080
    # Force width and height to be integers
    width = int(width)
    height = int(height)
    
    # Ensure minimum dimensions
    width = max(width, 1920)
    height = max(height, 1080)
    # Function to draw text with proper word wrapping
    def draw_wrapped_text(draw, text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Handle long words (like email addresses)
            if '@' in word:
                parts = word.replace('@', ' @ ').replace('.', ' . ').split()
                current_line.extend(parts)
            else:
                current_line.append(word)
            
            # Check if current line fits
            test_line = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            
            # Debug line width
            print(f"Line width: {line_width}, Max width: {max_width}, Line: {test_line}")
            
            if line_width > max_width:
                if len(current_line) > 1:
                    # Add all but the last word
                    lines.append(' '.join(current_line[:-1]))
                    current_line = current_line[-1:]
                else:
                    # Handle very long words
                    word = current_line[0]
                    while word:
                        found_part = False
                        for i in range(len(word), 0, -1):
                            part = word[:i]
                            bbox = draw.textbbox((0, 0), part, font=font)
                            part_width = bbox[2] - bbox[0]
                            if part_width <= max_width:
                                lines.append(part)
                                word = word[i:]
                                found_part = True
                                break
                        if not found_part:
                            # If no suitable part found, force split
                            lines.append(word[:1])
                            word = word[1:]
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Debug final lines
        print(f"Final wrapped lines: {lines}")
        return lines
    # Split text into parts if too long
    base_name, ext = os.path.splitext(output_filename)
    text_parts = split_long_text(text)
    generated_files = []
    
    # Use margins that work well for our layout
    margin_x = width * 0.08  # 8% horizontal margin for wider text
    margin_y = height * 0.12  # 12% vertical margin for better spacing
    max_width_area = width - 2 * margin_x
    max_height_area = height - 2 * margin_y
    
    # Calculate optimal font size based on text length
    def calculate_initial_font_size(text_length):
        # Base size on available height and estimated lines
        estimated_lines = max(1, text_length // 40)  # Estimate 40 chars per line for wider text
        available_height = max_height_area * 0.9  # Use 90% of height
        base_size = int(available_height / (estimated_lines * 1.1))  # 1.1 for tighter line spacing
        
        # Apply limits - increased for larger text
        if text_length < 100:
            return min(250, base_size)  # Cap at 250
        elif text_length < 200:
            return min(200, base_size)  # Cap at 200
        elif text_length < 300:
            return min(180, base_size)  # Cap at 180
        else:
            return min(160, base_size)  # Cap at 160
    
    # Find the optimal font size that works for all parts
    min_main_font_size = float('inf')
    for part in text_parts:
        main_text = part.upper()
        initial_size = calculate_initial_font_size(len(main_text))
        
        # Debug size calculation
        print(f"Initial size for part: {initial_size}, text length: {len(main_text)}")
        
        # Calculate font size with 95% of space
        font_size = get_font_size_that_fits(
            main_text,
            max_width_area * 0.95,  # Use 95% of available width
            max_height_area * 0.95,  # Use 95% of available height
            max_size=max(initial_size, 250)  # Ensure minimum max size of 250
        )
        min_main_font_size = min(min_main_font_size, font_size)
        print(f"Font size for part: {font_size}, minimum so far: {min_main_font_size}")
    
    for i, part in enumerate(text_parts):
        # Create filename for each part
        if len(text_parts) > 1:
            # Ensure we have .png extension
            base_without_ext = base_name.replace('.png', '')
            current_filename = f"{base_without_ext}_{i+1}.png"
        else:
            # Make sure single file has .png extension
            current_filename = output_filename if output_filename.endswith('.png') else output_filename + '.png'
        
        # Extract prayer number and scripture reference
        prayer_num = parse_prayer_number(part)
        if prayer_num:
            pattern_prayer = re.compile(r'(?i)\bprayer\s+' + re.escape(prayer_num) + r'\b')
            part = pattern_prayer.sub('', part, count=1).strip()

        scripture_ref = parse_scripture_reference(part)
        if scripture_ref:
            part = re.sub(re.escape(scripture_ref), '', part, count=1).strip()

        part = re.sub(r'^[;:]\s*', '', part)

        header_parts = []
        if prayer_num:
            header_parts.append(f"PRAYER {prayer_num}")
        if scripture_ref:
            header_parts.append(scripture_ref.upper())
        header_text = " | ".join(header_parts)

        # Create the image for this part
        img = create_gradient_background(width, height)
        
        # Add logo
        logo_path = os.path.join('static', 'logos', 'WIN LOGO.png')
        img = add_logo(img, logo_path)
        
        draw = ImageDraw.Draw(img)

        # Use 85% of screen space
        margin = 0.15  # 15% margin (85% usable space)
        margin_x = width * margin
        margin_y = height * margin
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

        main_text = part.upper()

        # Use the pre-calculated font size
        main_font_size = min_main_font_size

        # Get the font path - handle both local and Vercel environments
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_paths = [
            os.path.join(current_dir, 'fonts', 'ArialBold.ttf'),  # Local development path
            os.path.join('fonts', 'ArialBold.ttf'),  # Vercel path (relative to /api)
            os.path.join(current_dir, 'api', 'fonts', 'ArialBold.ttf'),  # Alternative local path
            "Arial Bold",  # System font fallback
            "Arial",  # Another system font fallback
        ]
        
        # Debug font paths
        print(f"Trying font paths: {font_paths}")
        
        title_font = None
        main_font = None
        errors = []
        
        for font_path in font_paths:
            try:
                if title_font_size > 0 and not title_font:
                    try:
                        title_font = ImageFont.truetype(font_path, title_font_size)
                        print(f"Loaded title font from {font_path}")
                    except Exception as e:
                        errors.append(f"Failed to load title font from {font_path}: {e}")
                
                if not main_font:
                    try:
                        main_font = ImageFont.truetype(font_path, main_font_size)
                        print(f"Loaded main font from {font_path}")
                        break  # Exit once we have both fonts
                    except Exception as e:
                        errors.append(f"Failed to load main font from {font_path}: {e}")
            except Exception as e:
                errors.append(f"Error with font path {font_path}: {e}")
                continue
        
        if not main_font:
            print(f"Warning: Could not load any fonts: {'; '.join(errors)}")
            print("Using default font as fallback")
            main_font = ImageFont.load_default()
            title_font = main_font

        y_cursor = margin_y

        if header_text and title_font:
            bbox_title = draw.textbbox((0, 0), header_text, font=title_font)
            header_width = bbox_title[2] - bbox_title[0]
            x_header = (width - header_width) / 2

            for offset in range(1, 3):
                draw.text((x_header + offset, y_cursor + offset), header_text, font=title_font, fill=(0, 0, 0))
            draw.text((x_header, y_cursor), header_text, font=title_font, fill="white")
            y_cursor += (bbox_title[3] - bbox_title[1]) + (title_font_size * 0.2)

        # Process and draw the main text
        try:
            # Split and process words
            words = main_text.split()
            processed_words = []
            for word in words:
                if '@' in word:
                    # Split email address at @ and . while keeping the symbols
                    parts = []
                    current = ''
                    for char in word:
                        if char in ['@', '.']:
                            if current:
                                parts.append(current)
                            parts.append(char)
                            current = ''
                        else:
                            current += char
                    if current:
                        parts.append(current)
                    processed_words.extend(parts)
                else:
                    processed_words.append(word)
            
            # Rejoin with spaces and measure
            main_text = ' '.join(processed_words)
            temp_img = Image.new('RGB', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            text_height, lines = measure_text_height(main_text, main_font, max_width_area, temp_draw, 0.05)
            
            # Calculate vertical position
            remaining_height = height - y_cursor - margin_y
            y_cursor += max(0, (remaining_height - text_height) / 2)
            
            # Set line spacing
            line_spacing = int(main_font.size * 0.2)  # Increased line spacing
            
            # Draw each line
            for line in lines:
                bbox_line = draw.textbbox((0, 0), line, font=main_font)
                line_width = bbox_line[2] - bbox_line[0]
                x_line = (width - line_width) / 2
                
                # Draw shadow and text
                for offset in range(1, 3):
                    draw.text((x_line + offset, y_cursor + offset), line, font=main_font, fill=(0, 0, 0))
                draw.text((x_line, y_cursor), line, font=main_font, fill="white")
                
                y_cursor += (bbox_line[3] - bbox_line[1]) + line_spacing
        except Exception as e:
            print(f"Error drawing text: {e}")
            raise

        img.save(current_filename, "PNG")
        generated_files.append(current_filename)
        print(f"Image saved as {current_filename}")
    
    return generated_files

# Ensure the output directory exists
if not os.path.exists("static/generated"):
    os.makedirs("static/generated", exist_ok=True)