# services/api/cv_handler.py - add download endpoint
from flask import Flask, request, jsonify, send_file
import os
import uuid
from pathlib import Path
import json

app = Flask(__name__)
STORAGE="./storage"
Path(STORAGE).mkdir(parents=True, exist_ok=True)

@app.route('/v1/tenants/<tenant_id>/cv/upload', methods=['POST'])
def upload_cv(tenant_id):
    f = request.files.get('file')
    job_title = request.form.get('job_title')
    industry = request.form.get('industry')
    if not f:
        return jsonify({'error':'file missing'}), 400
    job_id = str(uuid.uuid4())
    filename = f.filename
    save_path = os.path.join(STORAGE, job_id + '_' + filename)
    f.save(save_path)

    # Persist CV job record to DB. For dev, write to local jobs dir
    jobs_dir = os.path.join(STORAGE, 'jobs')
    Path(jobs_dir).mkdir(parents=True, exist_ok=True)
    job_record = {
        'id': job_id,
        'tenant_id': tenant_id,
        'user_id': None,
        'original_filename': filename,
        'storage_path': save_path,
        'job_title': job_title,
        'industry': industry,
        'status': 'pending'
    }
    Path(os.path.join(jobs_dir, job_id + '.json')).write_text(json.dumps(job_record))

    # In prod: push message to Kafka for worker

    return jsonify({'job_id': job_id}), 202

@app.route('/v1/tenants/<tenant_id>/cv/<job_id>')
def get_job(tenant_id, job_id):
    jobs_dir = os.path.join(STORAGE, 'jobs')
    p = Path(os.path.join(jobs_dir, job_id + '.json'))
    if not p.exists():
        return jsonify({'error':'not found'}), 404
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
        return jsonify({'error':'not found'}), 404
    jr = json.loads(p.read_text())
    pdf = jr.get('result_pdf_path')
    txt = jr.get('result_text_path')
    if pdf and os.path.exists(pdf):
        return send_file(pdf, as_attachment=True)
    elif txt and os.path.exists(txt):
        return send_file(txt, as_attachment=True)
    else:
        return jsonify({'error':'result not ready'}), 202

if __name__ == '__main__':
    app.run(port=8090)
