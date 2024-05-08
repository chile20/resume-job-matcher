from openai import OpenAI
import os
import re
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)


def format_text(text):
    # Apply formatting to bold markdown text
    formatted_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

    # Check if there are any <strong> tags
    if '<strong>' in formatted_text:
        # Split text around <strong> and </strong> tags
        split_text = re.split(r'(?=<strong>|</strong>)', formatted_text.strip())
    else:
        # If no <strong> tags, split by list item numbers, ensuring to catch multi-digit numbers and potential spaces after dots
        split_text = re.split(r'(?=\d+\.\s)', formatted_text.strip())

    return split_text


def refine_resume(resume, job_description):
    keywords = extract_keywords(job_description)
    if keywords:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user",
                     "content": f"You are a detail-oriented assistant tasked with providing specific improvements to enhance a resume. "
                                f"Review the provided resume and, focusing on the key qualifications and important skill sets listed from "
                                f"the job description: {keywords}, suggest targeted changes that address these aspects. "
                                f"Present your suggestions as a numbered list of 6 items at most. Ensure each suggestion aims to align "
                                f"the resume more closely with these particular job requirements and enhances the portrayal of relevant "
                                f"skills. Here’s the resume: {resume}."}
                ]
            )
            print("\nResult of suggestion is: \n")
            print(response.choices[0].message.content)
            formatted_result = format_text(response.choices[0].message.content)
            return formatted_result
        except Exception as e:
            return str(e)
    else:
        return "No keywords extracted. Check the job description."


def extract_keywords(job_description):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an applicant tracking system."},
                {"role": "user",
                 "content": f"Using the job description I provide, extract the most important keywords and terms. For each keyword or term, provide your logic for why you chose them. The job description is: {job_description}"}
            ]
        )
        print("\nResult of keywords is: \n")
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    except Exception as e:
        return str(e)
