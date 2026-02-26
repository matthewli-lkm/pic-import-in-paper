from flask import Blueprint, render_template, request, send_file, current_app, url_for, jsonify, flash
import os
import tempfile
import fitz
from werkzeug.utils import secure_filename
from unified_doc_tool.utils.image_utils import make_white_transparent

cropper_bp = Blueprint('cropper', __name__, url_prefix='/cropper')

@cropper_bp.route('/', methods=['GET'])
def index():
    return render_template('cropper.html')

@cropper_bp.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return {"error": "No file uploaded"}, 400
    
    filename = secure_filename(file.filename)
    if not (filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf'))):
         return {"error": "Invalid file type. Allowed: png, jpg, jpeg, pdf"}, 400

    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    response_data = {}
    
    if filename.lower().endswith('.pdf'):
        try:
            doc = fitz.open(file_path)
            num_pages = len(doc)
            
            # Convert first page by default
            page = doc[0]
            pix = page.get_pixmap() # Render high quality
            output_filename = f"{os.path.splitext(filename)[0]}_page_1.png"
            output_path = os.path.join(upload_folder, output_filename)
            pix.save(output_path)
            doc.close()
            
            response_data['is_pdf'] = True
            response_data['num_pages'] = num_pages
            response_data['pdf_filename'] = filename
            response_data['image_url'] = url_for('static_uploads', filename=output_filename)
        except Exception as e:
            return {"error": "Failed to process PDF."}, 500
    else:
        response_data['is_pdf'] = False
        response_data['image_url'] = url_for('static_uploads', filename=filename)

    return jsonify(response_data)

@cropper_bp.route('/get_page', methods=['POST'])
def get_page():
    data = request.json
    filename = secure_filename(data.get('filename'))
    page_num = int(data.get('page', 1)) - 1 # 0-indexed
    
    if not filename:
        return {"error": "No filename provided"}, 400
        
    upload_folder = current_app.config['UPLOAD_FOLDER']
    pdf_path = os.path.join(upload_folder, filename)
    
    if not os.path.exists(pdf_path):
        return {"error": "File not found"}, 404
        
    try:
        doc = fitz.open(pdf_path)
        if page_num < 0 or page_num >= len(doc):
            return {"error": "Page out of range"}, 400
            
        page = doc[page_num]
        pix = page.get_pixmap()
        output_filename = f"{os.path.splitext(filename)[0]}_page_{page_num + 1}.png"
        output_path = os.path.join(upload_folder, output_filename)
        pix.save(output_path)
        doc.close()
        return jsonify({"image_url": url_for('static_uploads', filename=output_filename)})
        
    except Exception as e:
        return {"error": "Failed to render page."}, 500
        
        return jsonify({"image_url": url_for('static_uploads', filename=output_filename)})
    except Exception as e:
        return {"error": str(e)}, 500

@cropper_bp.route('/process', methods=['POST'])
def process():
    file = request.files.get('cropped_image')
    action = request.form.get('action', 'download') # download or save
    
    if not file:
        return 'No file uploaded', 400
        
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_in:
        file.save(temp_in.name)
        temp_in.flush()
        
        # Apply transparency
        if action == 'save':
             # Save to shared assets
            filename = f"cropped_asset_{len(os.listdir(current_app.config['SHARED_ASSETS_FOLDER'])) + 1}.png"
            output_path = os.path.join(current_app.config['SHARED_ASSETS_FOLDER'], filename)
            make_white_transparent(temp_in.name, output_path)
            return jsonify({"status": "success", "filename": filename})
        else:
            # Prepare for download
            temp_out = temp_in.name.replace('.png', '_transparent.png')
            make_white_transparent(temp_in.name, temp_out)
            return send_file(temp_out, mimetype='image/png', as_attachment=True, download_name='cropped_transparent.png')
