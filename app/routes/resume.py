import io
import json
import os
from dotenv import load_dotenv
from fastapi import APIRouter, File, UploadFile
from groq import Groq
from pypdf import PdfReader

from app.models.interview_request import InterviewRequest
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

router = APIRouter()

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    content=await file.read()
    pdf_reader = PdfReader(io.BytesIO(content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return {
        "filename": file.filename, 
        "content_type": file.content_type,
        "extracted_text": text # Return only the first 500 characters for preview
        }

@router.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    contents = await file.read()
    pdf_reader = PdfReader(io.BytesIO(contents))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    prompt = f"""
Analyze the following resume text.

Return response strictly in JSON format like this:
{{
  "score": number,
  "strengths": [list of strengths],
  "weaknesses": [list of weaknesses],
  "improvements": [list of suggestions]
}}

Resume:
{text}
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # Use the appropriate model
        messages=[{
            "role": "system",
            "content": "You are a helpful assistant analyzing resumes."
        }, {
            "role": "user",
            "content": prompt
        }],
        temperature=0,
        response_format={"type": "json_object"}

    )
    print("RAW RESPONSE:")
    print(response.choices[0].message.content)
    analysis_data = json.loads(response.choices[0].message.content)

    return analysis_data
   # return {
    #"analysis": response.choices[0].message.content
#}
@router.post("/generate-questions")
async def generate_questions(request: InterviewRequest):

    prompt = f"""
    Generate interview questions for:
    Role: {request.role}
    Experience Level: {request.experience_level}

    Return JSON format:
    {{
        "technical_questions": [],
        "scenario_questions": [],
        "hr_questions": []
    }}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an expert technical interviewer. Return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)
