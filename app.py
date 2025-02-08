from flask import Flask, render_template, request, send_file, send_from_directory
from prayer_image import create_prayer_image
import os
from datetime import datetime
import io

app = Flask(__name__)

# Ensure the uploads directory exists
UPLOAD_FOLDER = 'static/generated'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/generated/<path:filename>')
def serve_image(filename):
    # Ensure filename has .png extension
    if not filename.endswith('.png'):
        filename = filename + '.png'
    
    response = send_from_directory('static/generated', filename)
    response.headers.set('Content-Type', 'image/png')
    response.headers.set('Content-Disposition', f'attachment; filename="{filename}"')
    return response

@app.route('/generate', methods=['POST'])
def generate():
    text = request.form.get('text', '')
    if not text:
        return {'error': 'No text provided'}, 400
    
    # Split by newlines first
    prayers = [prayer.strip() for prayer in text.split('\n') if prayer.strip()]
    
    # Generate images
    image_urls = []
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        for i, prayer in enumerate(prayers):
            # Generate unique filename for each prayer
            base_filename = f'prayer_{timestamp}_{i}.png'
            output_path = os.path.join(UPLOAD_FOLDER, base_filename)
            
            # Generate image(s) for this prayer - might return multiple files if prayer is long
            generated_files = create_prayer_image(prayer, output_filename=output_path)
            
            # Convert local file paths to URLs
            for filepath in generated_files:
                filename = os.path.basename(filepath)
                image_urls.append(f'/static/generated/{filename}')
                
    except Exception as e:
        return {'error': str(e)}, 500
    
    return {'image_urls': image_urls}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
