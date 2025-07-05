
# memory_sync_backend.py
# Flask-based memory sync bridge with metadata extraction and redaction integration

from flask import Flask, jsonify, request, send_from_directory
import os
import json
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# CONFIG
MEMORY_ROOT = "vault/memory"
REGISTRY_FILE = "vault/registry/memory_index.json"
EXHIBIT_DIR = "vault/exhibits"
REDACTION_QUEUE = "vault/redaction/queue"

# Ensure directories exist
os.makedirs(MEMORY_ROOT, exist_ok=True)
os.makedirs(os.path.dirname(REGISTRY_FILE), exist_ok=True)
os.makedirs(EXHIBIT_DIR, exist_ok=True)
os.makedirs(REDACTION_QUEUE, exist_ok=True)

# Load or initialize registry
if os.path.exists(REGISTRY_FILE):
    with open(REGISTRY_FILE, 'r') as f:
        memory_index = json.load(f)
else:
    memory_index = {}

# --- API ROUTES --- #

@app.route("/admin/sync", methods=["GET"])
def sync_memory():
    # Scan memory vault and update index
    updated = 0
    for root, dirs, files in os.walk(MEMORY_ROOT):
        for file in files:
            path = os.path.join(root, file)
            rel_path = os.path.relpath(path, MEMORY_ROOT)
            if rel_path not in memory_index:
                memory_index[rel_path] = {
                    "filename": file,
                    "path": rel_path,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "tags": [],
                    "status": "new"
                }
                updated += 1

    with open(REGISTRY_FILE, 'w') as f:
        json.dump(memory_index, f, indent=2)

    return jsonify({"synced": True, "new_entries": updated, "total": len(memory_index)})

@app.route("/vault/bridge/files", methods=["GET"])
def list_memory():
    return jsonify(memory_index)

@app.route("/vault/bridge/file/<path:filename>", methods=["GET"])
def serve_memory_file(filename):
    return send_from_directory(MEMORY_ROOT, filename, as_attachment=True)

@app.route("/vault/bridge/redact", methods=["POST"])
def queue_redaction():
    data = request.json
    file_to_redact = data.get("filename")
    if file_to_redact in memory_index:
        memory_index[file_to_redact]["status"] = "queued-for-redaction"
        with open(os.path.join(REDACTION_QUEUE, secure_filename(file_to_redact)), 'w') as f:
            f.write(file_to_redact)
        with open(REGISTRY_FILE, 'w') as f:
            json.dump(memory_index, f, indent=2)
        return jsonify({"queued": True, "file": file_to_redact})
    return jsonify({"queued": False, "reason": "File not in index"})

@app.route("/vault/bridge/exhibit", methods=["POST"])
def tag_exhibit():
    data = request.json
    filename = data.get("filename")
    label = data.get("label")
    if filename in memory_index:
        memory_index[filename]["tags"].append(label)
        with open(REGISTRY_FILE, 'w') as f:
            json.dump(memory_index, f, indent=2)
        return jsonify({"tagged": True})
    return jsonify({"tagged": False, "reason": "File not found"})

if __name__ == "__main__":
    app.run(debug=True)
