# DocPortal: Unified Document Processing Tool

DocPortal is a Flask-based web application designed to streamline document and image manipulation tasks. It consolidates multiple utility tools into a single, cohesive interface, allowing for efficient processing of PDFs and images.

## Features

### 1. Image Cropper & Transparency
*   **Upload & Crop:** Upload images or PDFs (first page) and crop specific areas using an interactive UI.
*   **Auto-Transparency:** Automatically converts white backgrounds to transparent, perfect for preparing logos or signatures.
*   **Asset Library:** Save cropped images to a "Shared Asset" library for immediate use in the Watermarker tool.

### 2. PDF to JPG Converter
*   **Bulk Conversion:** Converts every page of a PDF file into high-quality JPEG images.
*   **Zip Download:** Automatically bundles all converted images into a single ZIP file for easy download.

### 3. PDF Watermarker
*   **Branding:** Insert logos or watermarks onto every page of a PDF.
*   **Live Preview:** Visualize exactly where the watermark will appear on the first page before processing the entire document.
*   **Shared Assets:** Seamlessly use logos cropped in the Image Cropper tool.
*   **Position Control:** Precise X/Y offset controls to place your watermark exactly where needed.

## Tech Stack
*   **Backend:** Python, Flask
*   **PDF Processing:** PyMuPDF (fitz) - *Fast and efficient PDF rendering and manipulation.*
*   **Image Processing:** Pillow (PIL)
*   **Frontend:** HTML5, Bootstrap 5, Cropper.js

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/DocPortal.git
    cd DocPortal
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    
    # Windows
    venv\Scripts\activate
    
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r unified_doc_tool/requirements.txt
    ```

## Usage

### Running the Application

*   **Windows:**
    Double-click `start.bat` or run in terminal:
    ```cmd
    start.bat
    ```

*   **Mac / Linux:**
    Make the script executable and run it:
    ```bash
    chmod +x start.sh
    ./start.sh
    ```

The application will start at `http://127.0.0.1:5000/`.

### Security & Privacy Features

*   **Auto-Cleanup:** To protect privacy and save disk space, the application automatically deletes uploaded and processed files that are older than **24 hours**. This runs on a background schedule.
*   **Debug Mode:** By default, the application runs in production mode (debug features disabled). To enable debug mode, set the environment variable `FLASK_DEBUG=true` before running.

## Project Structure


## Usage

1.  **Start the Application:**
    
    Windows users can simply double-click **`start.bat`**.
    
    Or run from the terminal:
    ```bash
    # Ensure you are in the root directory
    python unified_doc_tool/app.py
    ```

2.  **Open Browser:**
    Navigate to `http://127.0.0.1:5000`

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
