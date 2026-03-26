import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def analyze_resume(jd_text, resume_text):
    """
    Compares resume text with job description using Groq API (Llama3).
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

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

def generate_improved_resume(jd_text, resume_text):
    """
    Optional: Generates an improved ATS-friendly version of the resume text.
    """
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
    
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
