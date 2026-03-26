import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

generation_config = {
  "temperature": 0.1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
)

def analyze_resume(jd_text, resume_text):
    """
    Compares resume text with job description using Google Gemini.
    Calculates ATS score (0-100), missing keywords, and suggestions.
    """
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) and senior technical recruiter.
    Analyze the following Resume against the given Job Description.
    
    Calculate and provide:
    1. ATS Score out of 100 (overall match).
    2. Keyword match percentage.
    3. Skills match percentage.
    4. Missing keywords (crucial skills/terms in JD missing from Resume).
    5. Improvement suggestions (bullet enhancements, section-wise feedback).
    6. Suggested template style (e.g., "Classic", "Modern", "Creative").

    Respond EXACTLY with a valid JSON object matching this schema:
    {{
      "ats_score": 85,
      "keyword_match_percentage": 80,
      "skills_match_percentage": 75,
      "missing_keywords": ["Python", "AWS", "Docker"],
      "suggestions": ["Add metrics to bullet points", "Include a Summary section"],
      "recommended_template": "Modern Portfolio"
    }}

    Job Description:
    {jd_text}

    Resume:
    {resume_text}
    """

    response = model.generate_content(prompt)
    
    return json.loads(response.text)

def generate_improved_resume(jd_text, resume_text):
    """
    Optional: Generates an improved ATS-friendly version of the resume text.
    """
    text_model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    
    prompt = f"""
    You are an expert professional resume writer.
    Rewrite this resume to maximize the ATS score against the provided Job Description.
    Use strong action verbs, quantify achievements, and naturally integrate missing keywords.
    Keep all factual information accurate.
    
    Output the improved resume as plain formatted text.
    
    Job Description:
    {jd_text}

    Resume:
    {resume_text}
    """
    
    response = text_model.generate_content(prompt)
    
    return response.text
