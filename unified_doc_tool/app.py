from flask import Flask, render_template, send_from_directory
from unified_doc_tool.config import Config
from unified_doc_tool.routes.cropper import cropper_bp
from unified_doc_tool.routes.converter import converter_bp
from unified_doc_tool.routes.watermarker import watermarker_bp
from unified_doc_tool.utils.file_utils import start_periodic_cleanup
import os

app = Flask(__name__)
app.config.from_object(Config)

# Register Blueprints
app.register_blueprint(cropper_bp)
app.register_blueprint(converter_bp)
app.register_blueprint(watermarker_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<filename>')
def static_uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == '__main__':
    # Start auto-cleanup (deletes files older than 24h)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    start_periodic_cleanup(root_dir)

    # Security: Disable debug mode by default unless environment variable is set
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, port=5000)
