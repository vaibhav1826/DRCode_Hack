import os
import json
import threading
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from twilio_client import send_message
from parser import download_and_parse_pdf
from analyzer import analyze_resume, generate_improved_resume

load_dotenv()

app = Flask(__name__)

# Simple in-memory session (user_phone -> state_dict)
sessions = {}

# Session States
STATE_IDLE = 'IDLE'
STATE_AWAITING_JD = 'AWAITING_JD'
STATE_AWAITING_RESUME = 'AWAITING_RESUME'

def get_session(phone):
    if phone not in sessions:
        sessions[phone] = {'state': STATE_IDLE, 'jd_text': None, 'resume_text': None}
    return sessions[phone]

def process_resume_in_background(from_number, media_url, jd_text):
    """Processes the PDF and AI analysis in a background thread to avoid Twilio 15s timeout."""
    try:
        # Parse PDF
        resume_text = download_and_parse_pdf(media_url)
        
        # Analyze using OpenAI/Gemini
        analysis = analyze_resume(jd_text, resume_text)
        
        # Format Response
        feedback = f"*ATS Analysis Complete!*\n\n"
        feedback += f"🎯 *ATS Score:* {analysis.get('ats_score')}/100\n"
        feedback += f"🔑 *Keyword Match:* {analysis.get('keyword_match_percentage')}%\n"
        feedback += f"🛠 *Skills Match:* {analysis.get('skills_match_percentage')}%\n\n"
        
        feedback += f"*Missing Keywords:*\n- " + "\n- ".join(analysis.get('missing_keywords', [])) + "\n\n"
        
        feedback += f"*Improvement Suggestions:*\n"
        for i, suggestion in enumerate(analysis.get('suggestions', []), 1):
            feedback += f"{i}. {suggestion}\n"
            
        feedback += f"\n*Recommended Template Style:* {analysis.get('recommended_template')}\n\n"
        feedback += "Type 'reset' anytime to analyze a different resume and job description."
        
        send_message(from_number, feedback)
        
        # Reset session after successful analysis
        sessions.pop(from_number, None)

    except Exception as e:
        print(f"Error handling background request: {e}")
        send_message(from_number, f"Oops! I had trouble reading the PDF or analyzing. Please try again or type 'reset'.")

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Twilio Webhook Endpoint
    """
    incoming_msg = request.form.get('Body', '').strip()
    from_number = request.form.get('From', '')
    media_url = request.form.get('MediaUrl0', None)
    media_type = request.form.get('MediaContentType0', None)

    session = get_session(from_number)

    if incoming_msg.lower() == 'reset':
        sessions.pop(from_number, None)
        send_message(from_number, "Conversation reset. Send 'Hi' to start over.")
        return "OK", 200

    try:
        if session['state'] == STATE_IDLE:
            send_message(from_number, "Welcome to the AI Resume Optimizer! 🚀\nPlease reply with the **Job Description (JD)** text you want to apply for.")
            session['state'] = STATE_AWAITING_JD
            
        elif session['state'] == STATE_AWAITING_JD:
            if not incoming_msg and not media_url:
                send_message(from_number, "Please paste the Job Description text.")
                return "OK", 200
                
            session['jd_text'] = incoming_msg if incoming_msg else "JD provided as document"
            session['state'] = STATE_AWAITING_RESUME
            send_message(from_number, "Great! Now please upload your current **Resume** as a **PDF** document.")
            
        elif session['state'] == STATE_AWAITING_RESUME:
            if not media_url or 'pdf' not in media_type.lower():
                send_message(from_number, "Please upload a valid PDF document for your resume.")
                return "OK", 200
                
            send_message(from_number, "Received! Analyzing your resume against the JD... This may take a moment. ⏳")
            
            # Start background thread to avoid webhook timeout
            thread = threading.Thread(
                target=process_resume_in_background, 
                args=(from_number, media_url, session['jd_text'])
            )
            thread.start()

    except Exception as e:
        print(f"Error handling request: {e}")

    return "OK", 200

if __name__ == '__main__':
    app.run(port=3000, debug=True)

