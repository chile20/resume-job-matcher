from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, jsonify
from .models import refine_resume
import os
# import docx2txt
import pdfplumber

from dotenv import load_dotenv
load_dotenv()

main = Blueprint('main', __name__)

PASSWORD = os.environ.get('PASSWORD')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('main.home'))
        else:
            return 'Invalid Password', 401
    return render_template('login.html')

@main.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    return render_template('home.html')

@main.route('/refine', methods=['POST'])
def refine():
    resume_text = extract_text_from_file(request.files.get('resume_file'), request.form['resume_text'])
    job_description_text = extract_text_from_file(request.files.get('job_description_file'), request.form['job_description_text'])
    print(resume_text)
    print(job_description_text)
    # Check if either the resume text or job description text is empty
    if not resume_text.strip() or not job_description_text.strip():
        return jsonify(error="Both resume and job description must be provided."), 400
    
    refined_text = refine_resume(resume_text, job_description_text)
    return jsonify(original=resume_text, refined=refined_text)
    # return render_template('result.html', original=resume_text, refined=refined_text)

def extract_text_from_file(file, fallback_texts):
    if file and file.filename != '':
        filename = file.filename.lower()
        if filename.endswith('.txt'):
            text_content = file.read().decode('utf-8')
        # elif filename.endswith('.docx'):
        #     text_content = docx2txt.process(file)
        elif filename.endswith('.pdf'):
            with pdfplumber.open(file) as pdf:
                text_content = '\n'.join(page.extract_text() for page in pdf.pages if page.extract_text())
        else:
            return "Unsupported file type", 400
        return text_content
    else:
        return fallback_texts
