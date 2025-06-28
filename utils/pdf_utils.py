import fitz  # PyMuPDF
import os
from PIL import Image

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''
    chapters = []
    
    # Extract text from each page and detect chapters (based on headings)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text("text")
        
        # Example chapter detection (can be customized)
        if "Chapter" in page.get_text("text"):
            chapters.append(f"Chapter {len(chapters) + 1}")
    
    return text, chapters

def extract_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    
    # Extract images from each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Save the image as a file
            img_filename = f"image_{page_num+1}_{img_index+1}.png"
            
            base_dir = 'static/img'
            os.makedirs(base_dir, exist_ok=True)  # Ensure the directory exists

            img_path = os.path.join(base_dir, img_filename)
            with open(img_path, 'wb') as img_file:
                img_file.write(image_bytes)
            
            images.append(img_filename)
    
    return images
