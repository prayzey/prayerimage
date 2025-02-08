from flask import Flask, request, send_file, jsonify, send_from_directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prayer_image import create_prayer_image
import tempfile
from datetime import datetime
import base64

app = Flask(__name__, static_folder='../static')

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/api/generate', methods=['POST'])
def generate():
    try:
        text = request.form.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Create a temporary directory for the images
        with tempfile.TemporaryDirectory() as temp_dir:
            image_data = []
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            try:
                # Generate unique filename
                base_filename = f'prayer_{timestamp}.png'
                output_path = os.path.join(temp_dir, base_filename)
                
                # Generate image(s)
                generated_files = create_prayer_image(text, output_filename=output_path)
                
                # Read and encode each generated file
                for filepath in generated_files:
                    with open(filepath, 'rb') as f:
                        image_bytes = f.read()
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        image_data.append(image_base64)
                
                if not image_data:
                    return jsonify({'error': 'No images were generated'}), 500
                
                return jsonify({
                    'image_data': image_data
                })
            except Exception as inner_e:
                print(f"Error generating image: {str(inner_e)}")
                return jsonify({'error': str(inner_e)}), 500
    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/api', methods=['GET'])
def home():
    return 'Prayer Image Generator API is running!'

if __name__ == '__main__':
    app.run(port=5001)
