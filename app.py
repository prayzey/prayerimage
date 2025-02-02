from flask import Flask, render_template, request, send_file
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

@app.route('/generate', methods=['POST'])
def generate():
    text = request.form.get('text', '')
    if not text:
        return {'error': 'No text provided'}, 400
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'prayer_{timestamp}.png'
    output_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Generate the image
    create_prayer_image(text, output_filename=output_path)
    
    # Return the URL of the generated image
    return {'image_url': f'/static/generated/{filename}'}

if __name__ == '__main__':
    app.run(debug=True)
