from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
import zipfile
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'vault/uploads/mvps/'
REGISTRY_FILE = 'mvp_registry.json'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return redirect(url_for('mvp_upload'))

@app.route('/admin/mvp-upload', methods=['GET', 'POST'])
def mvp_upload():
    if request.method == 'POST':
        if 'zipfile' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['zipfile']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Try to extract
            try:
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    extract_path = os.path.join(UPLOAD_FOLDER, filename.replace('.zip', ''))
                    zip_ref.extractall(extract_path)
                status = 'success'
            except Exception as e:
                flash(f"Extraction failed: {e}")
                status = 'extract_failed'

            # Log to registry
            if os.path.exists(REGISTRY_FILE):
                with open(REGISTRY_FILE, 'r') as f:
                    registry = json.load(f)
            else:
                registry = []

            registry.append({
                'filename': filename,
                'upload_path': filepath,
                'uploaded_by': 'admin',
                'status': status
            })

            with open(REGISTRY_FILE, 'w') as f:
                json.dump(registry, f, indent=2)

            flash(f'{filename} uploaded and extracted.')
            return redirect(url_for('mvp_upload'))

    return render_template('admin/mvp_upload.html')

@app.route('/admin/view-uploads')
def view_uploads():
    root_dir = os.path.join('vault', 'uploads', 'mvps')
    upload_summary = []

    if not os.path.exists(root_dir):
        return "No uploads found."

    items = sorted(os.listdir(root_dir))
    for item in items:
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path):
            contents = os.listdir(item_path)
            upload_summary.append({
                'name': item,
                'is_dir': True,
                'contents': contents
            })
        elif item.endswith('.zip'):
            upload_summary.append({
                'name': item,
                'is_dir': False,
                'contents': ['(ZIP file)']
            })

    return render_template('admin/view_uploads.html', uploads=upload_summary)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
