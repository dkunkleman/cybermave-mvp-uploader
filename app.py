from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'

MEMORY_FOLDER = 'vault/memory/'
REGISTRY_FILE = 'vault/memory_registry.json'

os.makedirs(MEMORY_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return redirect(url_for('memory_upload'))

@app.route('/admin/memory-upload', methods=['GET', 'POST'])
def memory_upload():
    os.makedirs(MEMORY_FOLDER, exist_ok=True)

    if request.method == 'POST':
        if 'memoryfiles' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('memoryfiles')

        if not files or files[0].filename == '':
            flash('No files selected')
            return redirect(request.url)

        for file in files:
            filename = secure_filename(file.filename)
            filepath = os.path.join(MEMORY_FOLDER, filename)
            file.save(filepath)

            # Log to registry
            if os.path.exists(REGISTRY_FILE):
                with open(REGISTRY_FILE, 'r') as f:
                    registry = json.load(f)
            else:
                registry = []

            registry.append({
                'filename': filename,
                'status': 'uploaded'
            })

            with open(REGISTRY_FILE, 'w') as f:
                json.dump(registry, f, indent=2)

            flash(f'{filename} uploaded successfully.')

    return render_template('admin/memory_upload.html')

if __name__ == '__main__':
    app.run(debug=True)
