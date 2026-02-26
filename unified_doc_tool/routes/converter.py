from flask import Blueprint, render_template, request, send_file, current_app, flash
import os
import tempfile
from werkzeug.utils import secure_filename
from unified_doc_tool.utils.pdf_utils import pdf_to_images, create_zip_from_files

converter_bp = Blueprint('converter', __name__, url_prefix='/converter')

@converter_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash('No file part', 'danger')
            return render_template('converter.html')
        
        file = request.files['pdf_file']
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return render_template('converter.html')
        
        filename = secure_filename(file.filename)
        if not filename.lower().endswith('.pdf'):
            flash('Invalid file type. Only PDF allowed.', 'danger')
            return render_template('converter.html')

        if file:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            pdf_path = os.path.join(upload_folder, filename)
            file.save(pdf_path)
            
            try:
                # Create a temp dir for images
                with tempfile.TemporaryDirectory() as temp_dir:
                    image_paths = pdf_to_images(pdf_path, temp_dir)
                    
                    zip_filename = f"{os.path.splitext(filename)[0]}_jpgs.zip"
                    zip_path = os.path.join(current_app.config['PROCESSED_FOLDER'], zip_filename)
                    
                    create_zip_from_files(image_paths, zip_path)
                    
                    return send_file(zip_path, as_attachment=True)
            except Exception as e:
                flash(f"Error processing file: {str(e)}", 'danger')
                
    return render_template('converter.html')
