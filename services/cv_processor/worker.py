# services/cv_processor/worker.py
import os
import uuid
import time
import json
import requests
from pathlib import Path

# This worker processes uploaded CVs: extract text, call Ollama model for rewrite, store results.

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://ollama.internal:11434/v1/generate')
STORAGE_ROOT = os.getenv('STORAGE_ROOT', '/data')

def extract_text_from_file(path):
    # Simple extraction for PDF/DOCX/TXT; use Apache Tika or python-docx/pdfminer in prod
    suffix = Path(path).suffix.lower()
    if suffix == '.txt':
        return Path(path).read_text(encoding='utf-8')
    elif suffix == '.pdf':
        # placeholder: in prod use pdfminer.six or tika
        return 'PDF_TEXT_PLACEHOLDER'
    elif suffix in ('.docx', '.doc'):
        return 'DOCX_TEXT_PLACEHOLDER'
    return ''

def build_prompt(original_text, job_title, industry):
    system = f"You are an expert CV optimization assistant running on Ollama Qwen3.5-9B-DeepSeek. Rewrite the candidate's CV to optimally match the job title '{job_title}' in the '{industry}' industry. Preserve factual accuracy unless instructed otherwise. Provide an ATS-friendly plain-text resume and a short visual layout suggestion."
    user = f"Original CV:\n{original_text}\n\nProduce:\n1) ATS-optimized plain-text resume\n2) Short visual PDF layout notes (typography, spacing, color tone)\n3) Optional LinkedIn headline and About blurb (50-80 words)"
    return system + "\n\n" + user


def call_ollama(prompt):
    payload = {"model":"Qwen3.5-9B-DeepSeek","prompt":prompt,"max_tokens":1200,"temperature":0.0}
    resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()


def process_cv_job(job_record):
    job_id = job_record['id']
    file_path = job_record['storage_path']
    job_title = job_record.get('job_title','')
    industry = job_record.get('industry','')

    original_text = extract_text_from_file(file_path)
    prompt = build_prompt(original_text, job_title, industry)
    result = call_ollama(prompt)

    # result handling: assume result contains 'text' field with assistant reply
    assistant_text = result.get('text') or json.dumps(result)

    # Save result to disk (raw assistant output)
    results_dir = os.path.join(STORAGE_ROOT, 'cv_results')
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    out_txt = os.path.join(results_dir, f"{job_id}.txt")
    Path(out_txt).write_text(assistant_text, encoding='utf-8')

    # Parse structured sections from assistant_text
    ats_text = ''
    visual_notes = ''
    linkedin_blurb = ''
    try:
        parts = assistant_text.split('\n')
        current = None
        buf = []
        for line in parts:
            header = line.strip()
            if header == 'ATS_RESUME':
                if current and buf:
                    if current == 'ATS_RESUME':
                        ats_text = '\n'.join(buf)
                current = 'ATS_RESUME'
                buf = []
                continue
            if header == 'VISUAL_NOTES':
                if current == 'ATS_RESUME':
                    ats_text = '\n'.join(buf)
                current = 'VISUAL_NOTES'
                buf = []
                continue
            if header == 'LINKEDIN_BLURB':
                if current == 'VISUAL_NOTES':
                    visual_notes = '\n'.join(buf)
                current = 'LINKEDIN_BLURB'
                buf = []
                continue
            if header == 'KEYWORDS':
                if current == 'LINKEDIN_BLURB':
                    linkedin_blurb = '\n'.join(buf)
                current = 'KEYWORDS'
                buf = []
                continue
            buf.append(line)
        # flush
        if current == 'ATS_RESUME' and not ats_text:
            ats_text = '\n'.join(buf)
        elif current == 'VISUAL_NOTES' and not visual_notes:
            visual_notes = '\n'.join(buf)
        elif current == 'LINKEDIN_BLURB' and not linkedin_blurb:
            linkedin_blurb = '\n'.join(buf)
    except Exception as e:
        ats_text = assistant_text
        visual_notes = ''
        linkedin_blurb = ''

    # Generate HTML for visual resume using visual_notes and ats_text
    try:
        from weasyprint import HTML
        html_content = f"""
        <html>
        <head>
        <meta charset='utf-8'>
        <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color:#111; padding:40px; max-width:800px; margin:auto }}
        .name {{ font-size:28px; font-weight:700; margin-bottom:4px }}
        .title {{ font-size:14px; color:#666; margin-bottom:16px }}
        pre {{ font-family: monospace; white-space: pre-wrap; font-size:12px }}
        </style>
        </head>
        <body>
        <div class='name'>Reformatted Resume</div>
        <div class='title'>{job_title} — {industry}</div>
        <h3>Summary</h3>
        <pre>{linkedin_blurb}</pre>
        <h3>Experience & Skills</h3>
        <pre>{ats_text}</pre>
        <h3>Design Notes</h3>
        <pre>{visual_notes}</pre>
        </body>
        </html>
        """
        out_pdf = os.path.join(results_dir, f"{job_id}.pdf")
        HTML(string=html_content).write_pdf(out_pdf)
    except Exception as e:
        out_pdf = None

    # Update job record JSON to mark completed and attach result paths
    try:
        jobs_dir = os.path.join(STORAGE_ROOT, 'jobs')
        job_file = os.path.join(jobs_dir, f"{job_id}.json")
        if os.path.exists(job_file):
            jr = json.loads(Path(job_file).read_text())
            jr['status'] = 'completed'
            jr['result_text_path'] = out_txt
            jr['result_pdf_path'] = out_pdf
            jr['updated_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            Path(job_file).write_text(json.dumps(jr), encoding='utf-8')
    except Exception:
        pass

    # Return paths
    return {'text_path': out_txt, 'pdf_path': out_pdf}
