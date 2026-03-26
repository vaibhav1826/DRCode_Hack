import os
import requests
import pdfplumber
import tempfile
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

def download_and_parse_pdf(media_url):
    """
    Downloads a PDF from Twilio's MediaUrl and parses it using pdfplumber.
    """
    try:
        # Download the PDF using Twilio credentials
        response = requests.get(
            media_url, 
            auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            stream=True
        )
        response.raise_for_status()
        
        # Save to temp file because pdfplumber needs a file-like object or path
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            for chunk in response.iter_content(chunk_size=8192):
                temp_pdf.write(chunk)
            temp_pdf_path = temp_pdf.name
            
        # Extract text using pdfplumber
        text = ""
        with pdfplumber.open(temp_pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    
        # Clean up temp file
        os.remove(temp_pdf_path)
        
        return text.strip()
    except Exception as e:
        print(f"Error parsing PDF: {str(e)}")
        raise e
