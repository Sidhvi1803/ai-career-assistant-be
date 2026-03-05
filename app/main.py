from urllib import response
from fastapi import FastAPI, UploadFile,File
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
import io
from groq import Groq
import os
from dotenv import load_dotenv
import json

from app.models.interview_request import InterviewRequest

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AI Career Assistant API running"}




@app.post("/upload-resume/")
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

@app.post("/analyze-resume/")
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
@app.post("/generate-questions")
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
