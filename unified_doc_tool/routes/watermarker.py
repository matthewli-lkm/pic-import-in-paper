from flask import Blueprint, render_template, request, send_file, current_app, url_for, flash, jsonify
import os
import shutil
import fitz
from PIL import Image
from werkzeug.utils import secure_filename
from unified_doc_tool.utils.pdf_utils import insert_watermark_to_pdf, generate_pdf_preview_image

watermarker_bp = Blueprint('watermarker', __name__, url_prefix='/watermark')

def get_shared_assets():
    assets_dir = current_app.config['SHARED_ASSETS_FOLDER']
    files = [f for f in os.listdir(assets_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return files

@watermarker_bp.route('/', methods=['GET'])
def index():
    shared_assets = get_shared_assets()
    return render_template('watermarker.html', shared_assets=shared_assets)

@watermarker_bp.route('/preview', methods=['POST'])
def preview():
    # Handle files and params
    pdf = request.files.get('pdf_file')
    png_option = request.form.get('png_option', 'default')
    offset_x = int(request.form.get('offset_x', -30))
    offset_y = int(request.form.get('offset_y', 265))
    scale = float(request.form.get('scale', 1.0))
    
    if not pdf:
        return "Missing PDF", 400
        
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    # Save PDF temporarily
    pdf_filename = secure_filename(pdf.filename)
    if not pdf_filename.lower().endswith('.pdf'):
        return "Invalid file type. Only PDF allowed", 400

    pdf_path = os.path.join(upload_folder, f"preview_{pdf_filename}")
    pdf.save(pdf_path)
    
    # Determine PNG path
    if png_option == 'custom':
        png = request.files.get('png_file')
        if not png: return "Missing PNG", 400
        
        if not png.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            return "Invalid watermark image type", 400
            
        png_path = os.path.join(upload_folder, f"preview_custom.png")
        png.save(png_path)
    elif png_option == 'shared':
         asset_name = request.form.get('shared_asset_name')
         png_path = os.path.join(current_app.config['SHARED_ASSETS_FOLDER'], asset_name)
    else:
        return "Invalid Option", 400

    preview_filename = f"preview_{pdf_filename}.png"
    preview_path = os.path.join(current_app.config['PROCESSED_FOLDER'], preview_filename)
    
    try:
        generate_pdf_preview_image(pdf_path, png_path, preview_path, offset_x=offset_x, offset_y=offset_y, scale_factor=scale)
        return url_for('processed_file', filename=preview_filename)
    except Exception as e:
        # Log the full error but return a generic message to the user
        print(f"Error generating preview: {e}")
        return "Error: Could not generate preview. Please check your files.", 500

@watermarker_bp.route('/process', methods=['POST'])
def process():
    pdf = request.files.get('pdf_file')
    png_option = request.form.get('png_option', 'default')
    offset_x = int(request.form.get('offset_x', -30))
    offset_y = int(request.form.get('offset_y', 265))
    scale = float(request.form.get('scale', 1.0))
    
    if not pdf:
        flash("Please upload a PDF", 'danger')
        return index()

    upload_folder = current_app.config['UPLOAD_FOLDER']
    pdf_filename = secure_filename(pdf.filename)
    if not pdf_filename.lower().endswith('.pdf'):
        flash("Invalid file type. Only PDF allowed", 'danger')
        return index()

    pdf_path = os.path.join(upload_folder, pdf_filename)
    pdf.save(pdf_path)
    
    if png_option == 'custom':
        png = request.files.get('png_file')
        if not png.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            flash("Invalid watermark image type", 'danger')
            return index()

        png_path = os.path.join(upload_folder, secure_filename(png.filename))
        png.save(png_path)
    elif png_option == 'shared':
         asset_name = request.form.get('shared_asset_name')
         png_path = os.path.join(current_app.config['SHARED_ASSETS_FOLDER'], asset_name)
    else:
         flash("Invalid Option", 'danger')
         return index()

    output_filename = f"watermarked_{pdf_filename}"
    output_path = os.path.join(current_app.config['PROCESSED_FOLDER'], output_filename)
    
    insert_watermark_to_pdf(pdf_path, png_path, output_path, offset_x=offset_x, offset_y=offset_y, scale_factor=scale)
    
    return send_file(output_path, as_attachment=True)

@watermarker_bp.route('/interactive_preview_data', methods=['POST'])
def interactive_preview_data():
    pdf = request.files.get('pdf_file')
    png_option = request.form.get('png_option', 'custom')
    
    if not pdf:
        return {"error": "Missing PDF"}, 400

    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    # Process PDF
    pdf_filename = secure_filename(pdf.filename)
    if not pdf_filename.lower().endswith('.pdf'):
        return {"error": "Invalid PDF"}, 400
    pdf_path = os.path.join(upload_folder, f"temp_preview_{pdf_filename}")
    pdf.save(pdf_path)
    
    # render PDF background
    pdf_width_pts = 0
    pdf_height_pts = 0
    bg_filename = ""
    
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]
        rect = page.rect
        pdf_width_pts = rect.width
        pdf_height_pts = rect.height
        
        pix = page.get_pixmap() # Default resolution is usually 72 dpi (scale=1.0)
        bg_filename = f"bg_{pdf_filename}.png"
        bg_path = os.path.join(upload_folder, bg_filename)
        pix.save(bg_path)
        doc.close()
    except Exception as e:
        return {"error": f"Failed to render PDF: {e}"}, 500

    # Process PNG
    watermark_url = ""
    wm_width = 0
    wm_height = 0
    
    if png_option == 'custom':
        png = request.files.get('png_file')
        if png:
            if not png.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                return {"error": "Invalid Image"}, 400
            png_filename = f"temp_wm_{secure_filename(png.filename)}"
            png_path = os.path.join(upload_folder, png_filename)
            png.save(png_path)
            
            watermark_url = url_for('static_uploads', filename=png_filename)
            
            with Image.open(png_path) as img:
                wm_width, wm_height = img.size
    elif png_option == 'shared':
        asset_name = request.form.get('shared_asset_name')
        if asset_name:
            src = os.path.join(current_app.config['SHARED_ASSETS_FOLDER'], asset_name)
            if os.path.exists(src):
                # Copy to uploads for access
                dst_name = f"temp_wm_{asset_name}"
                dst = os.path.join(upload_folder, dst_name)
                shutil.copy(src, dst)
                watermark_url = url_for('static_uploads', filename=dst_name)
                
                with Image.open(dst) as img:
                    wm_width, wm_height = img.size

    return jsonify({
        "pdf_bg_url": url_for('static_uploads', filename=bg_filename),
        "pdf_width_pts": pdf_width_pts,
        "pdf_height_pts": pdf_height_pts,
        "watermark_url": watermark_url,
        "wm_width_px": wm_width,
        "wm_height_px": wm_height
    })
