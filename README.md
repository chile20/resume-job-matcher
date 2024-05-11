# Resume-Job Matcher

Resume-Job Matcher is a Flask web application designed to provide tailored suggestions for improving resumes based on specific job descriptions. By analyzing the job description, the application highlights key areas where a resume can be enhanced to better match the job requirements.

## Features

- Analyze job descriptions to extract key requirements.
- Suggest improvements and enhancements for resumes based on job descriptions.
- User-friendly and mobile responsive interface for uploading resumes and job descriptions.

## Prerequisites

- An OpenAI API key for accessing AI models.

## Local Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/chile20/resume-job-matcher
   cd resume-job-matcher
   ```
   
2. **Set up a Virtual Environment and Install Dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Environment Variables**

   Create a .env file in the root directory and add the following:

   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   PASSWORD=your_password_here
   SECRET_KEY=your_secret_key_here
   ```
   
4. **Run the Development Server**

   ```bash
   flask run
   ```
   
## Usage

+ **Upload a Resume and Job Description:** Navigate to the home page, where you can upload both a resume and the corresponding job description.
+ **Receive Suggestions:** The system will analyze the inputs and provide tailored suggestions to enhance the resume.

## License

This project is licensed under the MIT License - see the LICENSE file for details.