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

            # Extract ZIP contents
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(UPLOAD_FOLDER, filename.replace('.zip', '')))

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
                'status': 'success'
            })

            with open(REGISTRY_FILE, 'w') as f:
                json.dump(registry, f, indent=2)

            flash(f'{filename} uploaded and extracted.')
            return redirect(url_for('mvp_upload'))

    return render_template('admin/mvp_upload.html')

if __name__ == '__main__':
    app.run(debug=True)
