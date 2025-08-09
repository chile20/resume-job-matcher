"""
Simple and efficient resume optimizer with Gemini AI
"""

import google.generativeai as genai
import os
import re
import time
from typing import List, Optional
from dotenv import load_dotenv

# Load environment
load_dotenv()
api_key = os.getenv('GOOGLE_AI_API_KEY')

# Configuration
MODELS_TO_TRY = [
    'gemini-1.5-flash',
    'gemini-1.5-pro', 
    'gemini-pro'
]

GENERATION_CONFIG = {
    'temperature': 0.3,
    'max_output_tokens': 2048,
}

MAX_RETRIES = 3
RETRY_DELAY = 2

# Global model instance
current_model = None

def initialize_gemini():
    """Initialize Gemini with the first available model"""
    global current_model
    
    if not api_key:
        print("Warning: GOOGLE_AI_API_KEY not found")
        return False
    
    genai.configure(api_key=api_key)
    
    for model_name in MODELS_TO_TRY:
        try:
            test_model = genai.GenerativeModel(model_name)
            response = test_model.generate_content("Test")
            if response and response.text:
                current_model = test_model
                print(f"Using model: {model_name}")
                return True
        except Exception:
            continue
    
    print("Warning: No available Gemini models found")
    return False

def make_api_call(prompt: str) -> Optional[str]:
    """Make API call with retry logic"""
    if not current_model:
        return None
    
    for attempt in range(MAX_RETRIES):
        try:
            response = current_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(**GENERATION_CONFIG)
            )
            
            if response and response.text:
                return response.text
            
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle specific errors
            if "quota" in error_msg or "limit" in error_msg:
                return f"Error: Rate limit reached. Try again later."
            elif "safety" in error_msg:
                return f"Error: Content flagged by safety filters."
            elif attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                return f"Error: Service unavailable - {str(e)}"
    
    return None

def format_text(text: str) -> List[str]:
    """Format response text into list"""
    if not text or not isinstance(text, str):
        return [str(text)] if text else []
    
    # Apply bold formatting
    formatted = re.sub(r'(\*\*|"|\'|`)(.*?)\1', r'<strong>\2</strong>', text)
    
    # Split by numbered items
    items = re.split(r'(?=\d+\.\s)', formatted.strip())
    items = [item.strip() for item in items if item.strip()]
    
    return items if items else [formatted]

def extract_keywords(job_description: str) -> str:
    """Extract keywords from job description"""
    if not job_description.strip():
        return "Error: Empty job description"
    
    prompt = f"""
<system_role>
You are an advanced ATS keyword extraction specialist with deep expertise in parsing job descriptions and identifying the exact terms that automated screening systems prioritize for candidate ranking and visibility.
</system_role>

<task>
Analyze the provided job description and extract 15-20 strategically critical keywords that have the highest impact on ATS scoring and recruiter searches. Provide clear reasoning for each selection based on ATS prioritization patterns.
</task>

<input_data>
<job_description>
{job_description}
</job_description>
</input_data>

<extraction_methodology>
<priority_factors>
- Frequency of appearance (repeated terms indicate higher importance)
- Placement in critical sections (title, requirements, qualifications)
- Technical specificity (exact tools, languages, frameworks)
- Experience quantifiers (years, levels, certifications)
- Industry-standard terminology and buzzwords
- Action verbs describing core responsibilities
</priority_factors>

<ranking_criteria>
- **Critical**: Terms that directly determine pass/fail in ATS filtering
- **High**: Keywords that significantly boost ranking scores
- **Important**: Terms that provide competitive advantage in searches
</ranking_criteria>
</extraction_methodology>

<output_requirements>
<format>
**TECHNICAL SKILLS:**
- [skill]: [ATS importance reasoning and strategic value]

**QUALIFICATIONS:**
- [requirement]: [ATS importance reasoning and strategic value]

**RESPONSIBILITIES:**
- [keyword]: [ATS importance reasoning and strategic value]

**INDUSTRY TERMS:**
- [term]: [ATS importance reasoning and strategic value]
</format>

<quality_standards>
- Extract exactly 15-20 most impactful keywords total
- Prioritize terms that directly affect ATS ranking algorithms
- Explain the strategic value and ATS impact for each selection
- Group related terms logically within categories
- Focus on specific, searchable terms over generic language
- Include context about frequency or placement when relevant
</quality_standards>

<constraints>
- Total output: 15-20 keywords maximum across all categories
- Each reasoning should be 1 sentence explaining ATS/search impact
- Avoid generic words unless specifically emphasized in the job description
- Prioritize exact matches over synonyms for ATS optimization
</constraints>
</output_requirements>

<example_output>
**TECHNICAL SKILLS:**
- Python: Appears 8 times and listed as primary requirement, critical for ATS filtering
- AWS: Mentioned in both requirements and responsibilities, high-priority cloud keyword

**QUALIFICATIONS:**
- Bachelor's degree: Standard ATS filter criterion, essential for initial screening
- 5+ years experience: Specific experience threshold that ATS systems screen for
</example_output>
"""
    
    result = make_api_call(prompt)
    
    if result and not result.startswith("Error:"):
        print(f"\nKeywords extracted:\n{result}\n")
        return result
    else:
        # Simple fallback
        fallback = extract_keywords_fallback(job_description)
        print(f"\nKeywords (fallback):\n{fallback}\n")
        return fallback

def extract_keywords_fallback(job_description: str) -> str:
    """Simple keyword extraction fallback"""
    # Extract common technical terms
    skills_pattern = r'\b(?:Python|Java|JavaScript|React|Node\.js|SQL|AWS|Docker|Kubernetes|Git|Agile|Scrum|TypeScript|C\+\+|C#)\b'
    experience_pattern = r'\b\d+\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)\b'
    
    skills = re.findall(skills_pattern, job_description, re.IGNORECASE)
    experience = re.findall(experience_pattern, job_description, re.IGNORECASE)
    
    result = []
    if skills:
        result.append(f"**TECHNICAL SKILLS:**\n- {', '.join(set(skills))}: Core technologies mentioned")
    if experience:
        result.append(f"**QUALIFICATIONS:**\n- {', '.join(set(experience))}: Experience requirements")
    
    return "\n\n".join(result) if result else "**GENERAL:** Professional skills and relevant experience"

def refine_resume(resume: str, job_description: str) -> List[str]:
    """Generate resume improvement suggestions"""
    if not resume.strip() or not job_description.strip():
        return ["Error: Resume and job description cannot be empty"]
    
    # Get keywords first
    keywords = extract_keywords(job_description)
    
    if keywords.startswith("Error:"):
        return [keywords]
    
    prompt = f"""<system_role>
You are a resume optimization expert with 15+ years of experience in ATS systems and recruitment.
</system_role>

<task>
Using the pre-analyzed keyword insights, perform a comprehensive gap analysis between this resume and the target role requirements, then provide exactly 6 high-impact, specific improvements that will maximize ATS score and recruiter attention.
</task>

<input_data>
<extracted_keyword_analysis>
{keywords}
</extracted_keyword_analysis>

<current_resume>
{resume}
</current_resume>
</input_data>

<analysis_method>
1. Compare resume content against the provided keyword analysis and reasoning
2. Identify critical missing keywords that have high ATS importance
3. Find weak or generic language that needs strengthening with specific terms
4. Locate quantification opportunities in experience descriptions
5. Assess skills section alignment with the keyword priorities
6. Check for strategic keyword placement and density issues
</analysis_method>

<output_requirements>
<format>
Provide exactly 6 numbered suggestions:
1. **[Resume Section]** - [Specific actionable change with clear implementation guidance]

Then add:
7. **Critical Keywords to Include:** [Clean comma-separated list of the most important keywords extracted from the keyword analysis - no bold formatting, just the terms]
</format>

<quality_standards>
- Each suggestion must reference specific content from the resume
- Provide exact wording or phrases to add/change
- Base recommendations directly on the keyword analysis provided
- Include implementation priority (high/medium impact)
- Focus on incorporating the most strategically important keywords first
- Suggest specific metrics, numbers, or quantifiable achievements where possible
</quality_standards>

<constraints>
- Maximum 6 suggestions only
- Each suggestion 1-2 sentences maximum
- Section 7 should be a simple, clean list without explanations
- All recommendations must be based on the keyword analysis provided
- No assumptions about job requirements beyond what's in the keyword data
</constraints>
</output_requirements>

<example_output>
1. **Skills Section** - Add "Python, PostgreSQL, and Docker" prominently in your technical skills, as the keyword analysis shows these are critical technical requirements with high ATS importance.

7. **Critical Keywords to Include:** Python, PostgreSQL, Docker, agile methodology, CI/CD, RESTful APIs, microservices, AWS, team leadership, project management
</example_output>
"""
    
    result = make_api_call(prompt)
    
    if result and not result.startswith("Error:"):
        print(f"\nSuggestions generated:\n{result}\n")
        return format_text(result)
    else:
        # Fallback suggestions
        fallback = [
            "1. **Skills Section** - Update technical skills to match job requirements",
            "2. **Experience** - Add specific numbers and metrics to quantify achievements", 
            "3. **Summary** - Write a compelling 2-3 line summary highlighting relevant qualifications",
            "4. **Keywords** - Incorporate important terms from the job description",
            "5. **Action Verbs** - Use strong action words that demonstrate results and leadership",
            "6. **Format** - Ensure consistent formatting and ATS-friendly structure"
        ]
        print(f"\nSuggestions (fallback):\n")
        for suggestion in fallback:
            print(suggestion)
        return fallback

def refine_resume_production(resume: str, job_description: str) -> List[str]:
    """Production-ready function with automatic fallback"""
    try:
        result = refine_resume(resume, job_description)
        
        # Check if we got valid suggestions (not just errors)
        if (isinstance(result, list) and 
            len(result) > 0 and 
            not any("Error:" in str(item) for item in result)):
            return result
        else:
            # Use fallback
            return refine_resume("", "")  # This triggers fallback
            
    except Exception as e:
        print(f"Error: {e}")
        return refine_resume("", "")  # This triggers fallback

# Initialize on import
initialize_gemini()

# Test function
if __name__ == "__main__":
    # Test with sample data
    sample_job = "Software Engineer requiring Python, React, 3+ years experience, Bachelor's degree"
    sample_resume = "John Doe\nSoftware Developer\n2 years experience\nSkills: Python, HTML"
    
    print("Testing resume optimizer...")
    suggestions = refine_resume(sample_resume, sample_job)
    print(f"\nFinal suggestions: {len(suggestions)} items")