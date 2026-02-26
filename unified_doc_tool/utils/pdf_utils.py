import fitz  # PyMuPDF
from PIL import Image
import io
import os
import zipfile

def pdf_to_images(pdf_path, output_folder):
    """
    Converts all pages of a PDF to regular JPEG images.
    Returns a list of paths to the generated images.
    """
    doc = fitz.open(pdf_path)
    image_paths = []
    
    # Clean filename for prefix
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    for page_num, page in enumerate(doc):
        # Render page to an image
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 2x zoom for better quality
        output_filename = f"{base_name}_page_{page_num + 1}.jpg"
        output_path = os.path.join(output_folder, output_filename)
        pix.save(output_path)
        image_paths.append(output_path)
        
    doc.close()
    return image_paths

def create_zip_from_files(file_paths, zip_path):
    """
    Zips a list of files into a single zip archive.
    """
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in file_paths:
            zipf.write(file_path, os.path.basename(file_path))
    return zip_path

def insert_watermark_to_pdf(pdf_path, image_path, output_path, offset_x=0, offset_y=100, scale_factor=0.2):
    """
    Inserts an image watermark into every page of a PDF.
    """
    doc = fitz.open(pdf_path)
    img = Image.open(image_path)
    
    # Convert image to bytes for PyMuPDF
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    
    img_width, img_height = img.size

    for page in doc:
        rect = page.rect
        
        # Calculate size and position
        scale = min(rect.width / img_width, rect.height / img_height, 1) * scale_factor
        new_width = img_width * scale
        new_height = img_height * scale
        
        x0 = (rect.width - new_width) / 2 + offset_x
        y0 = (rect.height - new_height) / 2 + offset_y
        x1 = x0 + new_width
        y1 = y0 + new_height
        
        # Insert
        page.insert_image(fitz.Rect(x0, y0, x1, y1), stream=img_bytes)
        
    doc.save(output_path)
    doc.close()
    return output_path

def generate_pdf_preview_image(pdf_path, image_path, output_img_path, offset_x=0, offset_y=100, scale_factor=0.2):
    """
    Generates a preview image of the first page of the PDF with the watermark applied.
    """
    doc = fitz.open(pdf_path)
    if len(doc) == 0:
        return None
        
    page = doc[0]
    
    if image_path:
        img = Image.open(image_path)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        img_width, img_height = img.size
        rect = page.rect
        
        scale = min(rect.width / img_width, rect.height / img_height, 1) * scale_factor
        new_width = img_width * scale
        new_height = img_height * scale
        
        x0 = (rect.width - new_width) / 2 + offset_x
        y0 = (rect.height - new_height) / 2 + offset_y
        x1 = x0 + new_width
        y1 = y0 + new_height
        
        page.insert_image(fitz.Rect(x0, y0, x1, y1), stream=img_bytes)

    # Render the page to an image
    pix = page.get_pixmap()
    pix.save(output_img_path)
    doc.close()
    
    return output_img_path
