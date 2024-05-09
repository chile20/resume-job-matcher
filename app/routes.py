import pdfplumber
from flask import Blueprint, render_template, request, jsonify
from .models import refine_resume
import os
import docx2txt
from pdfplumber import open as open_pdf

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/refine', methods=['POST'])
def refine():
    resume_text = extract_text_from_file(request.files.get('resume_file'), request.form['resume_text'])
    job_description_text = extract_text_from_file(request.files.get('job_description_file'), request.form['job_description_text'])
    print(resume_text)
    print(job_description_text)
    refined_text = refine_resume(resume_text, job_description_text)
    return jsonify(original=resume_text, refined=refined_text)
    # return render_template('result.html', original=resume_text, refined=refined_text)


def extract_text_from_file(file, fallback_texts):
    if file and file.filename != '':
        filename = file.filename.lower()
        if filename.endswith('.txt'):
            text_content = file.read().decode('utf-8')
        elif filename.endswith('.docx'):
            text_content = docx2txt.process(file)
        elif filename.endswith('.pdf'):
            with pdfplumber.open(file) as pdf:
                text_content = '\n'.join(page.extract_text() for page in pdf.pages if page.extract_text())
        else:
            return "Unsupported file type", 400
        return text_content
    else:
        return fallback_texts
