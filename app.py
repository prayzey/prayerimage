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
    try:
        text = request.form.get('text', '')
        if not text:
            return {'error': 'No text provided'}, 400
        
        # Split by newlines first
        prayers = [prayer.strip() for prayer in text.split('\n') if prayer.strip()]
        
        # Generate images
        image_data = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for i, prayer in enumerate(prayers):
            try:
                # Generate unique filename for each prayer
                base_filename = f'prayer_{timestamp}_{i}.png'
                output_path = os.path.join(UPLOAD_FOLDER, base_filename)
                
                print(f"Generating image for prayer {i+1}: {prayer[:50]}...")
                
                # Generate image(s) for this prayer - might return multiple files if prayer is long
                generated_files = create_prayer_image(prayer, output_filename=output_path)
                print(f"Generated files: {generated_files}")
            except Exception as e:
                print(f"Error generating image {i+1}: {str(e)}")
                return {'error': f'Error generating image {i+1}: {str(e)}'}, 500
            
            # Convert images to base64
            for filepath in generated_files:
                with open(filepath, 'rb') as f:
                    image_bytes = f.read()
                    import base64
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                    image_data.append(image_base64)
                    
                # Clean up the file after converting to base64
                os.remove(filepath)
                
    except Exception as e:
        return {'error': str(e)}, 500
    
    return {'image_data': image_data}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
