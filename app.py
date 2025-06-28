from flask import Flask, render_template, request, redirect, url_for
from utils.pdf_utils import extract_text, extract_images
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf_file' not in request.files:
        return redirect(request.url)
    
    file = request.files['pdf_file']
    if file.filename == '':
        return redirect(request.url)
    
    os.makedirs('pdfs', exist_ok=True) 
    
    if file and file.filename.endswith('.pdf'):
        file_path = f"pdfs/{file.filename}"
        file.save(file_path)
        
        # Extract text and images from the PDF
        text, chapters = extract_text(file_path)
        images = extract_images(file_path)

        extracted_text_dir = 'extracted/text'
        os.makedirs(extracted_text_dir, exist_ok=True)  # Ensure the directory exists
        # Store extracted data
        extracted_text_path = f"{extracted_text_dir}/{file.filename}.txt"
        with open(extracted_text_path, 'w') as f:
            f.write(text)

        # Display results
        return render_template('results.html', text=text, chapters=chapters, images=images)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
