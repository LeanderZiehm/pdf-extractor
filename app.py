import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
from utils.pdf_utils import extract_text, extract_images
import dotenv
dotenv.load_dotenv()

app = Flask(__name__)

PDFS_DIR = 'pdfs'
TEXT_DIR = 'extracted/text'
SLUGS_FILE = 'slugs.json'
PORT = int(os.getenv('PORT', 5001))

os.makedirs(PDFS_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

def load_slugs():
    if os.path.exists(SLUGS_FILE):
        with open(SLUGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_slugs(slugs):
    with open(SLUGS_FILE, 'w') as f:
        json.dump(slugs, f, indent=4)

def generate_slug(text):
    return '_'.join(text.strip().split()[:10]).lower()



@app.route('/')
def index():
    pdfs = [f for f in os.listdir(PDFS_DIR) if f.endswith('.pdf')]
    slugs = load_slugs()  # load slugs from file
    return render_template('index.html', pdfs=pdfs, slugs=slugs)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf_file' not in request.files:
        return redirect(request.url)
    
    file = request.files['pdf_file']
    if file.filename == '':
        return redirect(request.url)
    
    if file and file.filename.endswith('.pdf'):
        file_path = os.path.join(PDFS_DIR, file.filename)
        file.save(file_path)
        
        text, _ = extract_text(file_path)
        
        text_path = os.path.join(TEXT_DIR, f"{file.filename}.txt")
        with open(text_path, 'w') as f:
            f.write(text)
            
        slugs = load_slugs()
        if file.filename not in slugs:
            slugs[file.filename] = generate_slug(text)
            save_slugs(slugs)

    return redirect(url_for('index'))

@app.route('/<slug>')
def pdf_view(slug):
    slugs = load_slugs()
    filename = None
    for f, s in slugs.items():
        if s == slug:
            filename = f
            break
    
    if not filename:
        return "PDF not found", 404

    text_path = os.path.join(TEXT_DIR, f"{filename}.txt")
    with open(text_path, 'r') as f:
        text = f.read()
        
    pdf_path = os.path.join(PDFS_DIR, filename)
    images = extract_images(pdf_path)
    
    return render_template('pdf_view.html', text=text, images=images, filename=filename, slug=slug)


@app.route('/edit_slug/<filename>', methods=['POST'])
def edit_slug(filename):
    new_slug = request.form.get('new_slug')
    existing_slugs = load_slugs()  # implement based on your logic

    if new_slug in existing_slugs:
        return jsonify({'status': 'error', 'message': 'Slug already exists'}), 400


    slugs = load_slugs()
    slugs[filename] = new_slug
    # Save new slug (rename file or update DB, etc.)
    save_slugs(slugs)
    
    return jsonify({'status': 'success', 'new_slug': new_slug})

@app.route('/delete/<filename>', methods=['POST'])
def delete_pdf(filename):
    pdf_path = os.path.join(PDFS_DIR, filename)
    text_path = os.path.join(TEXT_DIR, f"{filename}.txt")

    # Delete the PDF file
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    # Delete the extracted text
    if os.path.exists(text_path):
        os.remove(text_path)

    # Update slugs
    slugs = load_slugs()
    if filename in slugs:
        del slugs[filename]
        save_slugs(slugs)

    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True,port=PORT)
