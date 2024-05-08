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
    file = request.files.get('resume_file')
    if file and file.filename != '':
        filename = file.filename
        if filename.endswith('.txt'):
            resume_text = file.read().decode('utf-8')
        elif filename.endswith('.docx'):
            resume_text = docx2txt.process(file)
        elif filename.endswith('.pdf'):
            from pdfplumber import open as open_pdf
            with open_pdf(file) as pdf:
                resume_text = '\n'.join(page.extract_text() for page in pdf.pages if page.extract_text())
        else:
            return "Unsupported file type", 400
    else:
        resume_text = request.form['resume_text']
    job_description_text = request.form['job_description_text']
    print(resume_text)
    print(job_description_text)
    refined_text = refine_resume(resume_text, job_description_text)
    return jsonify(original=resume_text, refined=refined_text)
    # return render_template('result.html', original=resume_text, refined=refined_text)

def extract_text_from_file(file, fallback_text):
    if file and file.filename != '':
        filename = file.filename.lower()  # Use lower case to handle file extensions reliably
        if filename.endswith('.txt'):
            text = file.read().decode('utf-8')
        elif filename.endswith('.docx'):
            text = docx2txt.process(file)
        elif filename.endswith('.pdf'):
            with open_pdf(file) as pdf:
                text = '\n'.join(page.extract_text() for page in pdf.pages if page.extract_text())
        else:
            raise ValueError("Unsupported file type")
        return text
    else:
        return fallback_text
