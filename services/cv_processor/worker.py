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

    # Save result to disk
    out_path = os.path.join(STORAGE_ROOT, 'cv_results', f"{job_id}.txt")
    Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(assistant_text, encoding='utf-8')

    # In prod: update DB with result_text and result_pdf_path
    return out_path
