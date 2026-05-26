from flask import Flask, request, jsonify, send_file
import os
import uuid
from pathlib import Path
import json
import time
import shutil
import re

app = Flask(__name__)
STORAGE = "./storage"
Path(STORAGE).mkdir(parents=True, exist_ok=True)
start_time = time.time()

# Validation configuration
ALLOWED_EXT = {'.pdf', '.docx', '.doc', '.txt'}
MAX_FILE_BYTES = int(os.getenv('CV_MAX_BYTES', 5 * 1024 * 1024))  # 5 MB default
FILENAME_SAFE_RE = re.compile(r'[^A-Za-z0-9._-]')

try:
    import magic
    HAS_MAGIC = True
except Exception:
    HAS_MAGIC = False

def sanitize_filename(name: str) -> str:
    base = os.path.basename(name)
    return FILENAME_SAFE_RE.sub('_', base)

def detect_mime(path: str) -> str:
    if HAS_MAGIC:
        try:
            m = magic.Magic(mime=True)
            return m.from_file(path)
        except Exception:
            return ''
    # fallback: use extension mapping
    ext = Path(path).suffix.lower()
    if ext == '.pdf':
        return 'application/pdf'
    if ext in ('.doc', '.docx'):
        return 'application/msword'
    if ext == '.txt':
        return 'text/plain'
    return ''

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'uptime_seconds': int(time.time() - start_time)
    }), 200

@app.route('/ready')
def ready_check():
    # basic readiness: storage dir exists and writable
    try:
        test_file = os.path.join(STORAGE, '.ready')
        with open(test_file, 'w') as f:
            f.write('ok')
        os.remove(test_file)
        return jsonify({'ready': True}), 200
    except Exception as e:
        return jsonify({'ready': False, 'error': str(e)}), 500

@app.route('/v1/tenants/<tenant_id>/cv/upload', methods=['POST'])
def upload_cv(tenant_id):
    f = request.files.get('file')
    job_title = request.form.get('job_title')
    industry = request.form.get('industry')
    if not f:
        return jsonify({'error': 'file missing'}), 400

    # sanitize filename and write to tmp path first
    job_id = str(uuid.uuid4())
    filename = sanitize_filename(f.filename or f"upload_{job_id}")
    tmp_dir = os.path.join(STORAGE, 'tmp')
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, job_id + '_' + filename)
    f.save(tmp_path)

    # Size validation
    size = os.path.getsize(tmp_path)
    if size > MAX_FILE_BYTES:
        os.remove(tmp_path)
        return jsonify({'error': 'file too large'}), 413

    # MIME/type validation
    mime = detect_mime(tmp_path)
    ext = Path(tmp_path).suffix.lower()
    if ext not in ALLOWED_EXT:
        os.remove(tmp_path)
        return jsonify({'error': 'unsupported file extension'}), 415

    # Basic MIME match (best effort)
    if mime:
        if 'pdf' in mime and ext != '.pdf':
            os.remove(tmp_path)
            return jsonify({'error': 'mime mismatch'}), 415

    # Move to final storage
    final_path = os.path.join(STORAGE, job_id + '_' + filename)
    shutil.move(tmp_path, final_path)

    # Persist CV job record to DB. For dev, write to local jobs dir
    jobs_dir = os.path.join(STORAGE, 'jobs')
    Path(jobs_dir).mkdir(parents=True, exist_ok=True)
    job_record = {
        'id': job_id,
        'tenant_id': tenant_id,
        'user_id': None,
        'original_filename': filename,
        'storage_path': final_path,
        'job_title': job_title,
        'industry': industry,
        'status': 'pending',
        'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }
    Path(os.path.join(jobs_dir, job_id + '.json')).write_text(json.dumps(job_record))

    # In prod: push message to Kafka for worker

    return jsonify({'job_id': job_id}), 202

@app.route('/v1/tenants/<tenant_id>/cv/<job_id>')
def get_job(tenant_id, job_id):
    jobs_dir = os.path.join(STORAGE, 'jobs')
    p = Path(os.path.join(jobs_dir, job_id + '.json'))
    if not p.exists():
        return jsonify({'error': 'not found'}), 404
    job_record = json.loads(p.read_text())

    # Attach result if available
    result_path = os.path.join(STORAGE, 'cv_results', f"{job_id}.txt")
    if os.path.exists(result_path):
        job_record['status'] = 'completed'
        job_record['result_preview'] = Path(result_path).read_text()[:1000]
    return jsonify(job_record)

@app.route('/v1/tenants/<tenant_id>/cv/<job_id>/download')
def download_result(tenant_id, job_id):
    jobs_dir = os.path.join(STORAGE, 'jobs')
    p = Path(os.path.join(jobs_dir, job_id + '.json'))
    if not p.exists():
        return jsonify({'error': 'not found'}), 404
    jr = json.loads(p.read_text())
    pdf = jr.get('result_pdf_path')
    txt = jr.get('result_text_path')
    if pdf and os.path.exists(pdf):
        return send_file(pdf, as_attachment=True)
    elif txt and os.path.exists(txt):
        return send_file(txt, as_attachment=True)
    else:
        return jsonify({'error': 'result not ready'}), 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)
