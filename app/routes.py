from flask import Blueprint, render_template, request
from .models import refine_resume

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/refine', methods=['POST'])
def refine():
    resume_text = request.form['resume_text']
    job_description_text = request.form['job_description_text']
    refined_text = refine_resume(resume_text, job_description_text)
    return render_template('result.html', original=resume_text, refined=refined_text)
