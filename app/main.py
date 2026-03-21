
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import resume



app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-career-assistant-fe.netlify.app",
                   "http://localhost:5173",
                   "http://127.0.0.1:5173",
                   "https://ai-career-assistant-be-production.up.railway.app",
                   "http://127.0.0.1:8000",
                   "http://localhost:8000",
    
                   ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router, prefix="/resume", tags=["Resume"])

@app.get("/")
def root():
    return {"message": "AI Career Assistant API running"}


