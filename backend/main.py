from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
from typing import Any
from fastapi.params import Body
import logging 
logging.basicConfig(filename="app.log", level=logging.DEBUG)
from transformers import GPT2Tokenizer, GPT2LMHeadModel, TextGenerationPipeline
import torch


# Load environment variables from .env file (if any)
load_dotenv()

from typing import Optional

class Response(BaseModel):
    #result: Optional[str]
    result: str

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000"
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nlp = pipeline("text-generation", model="gpt2")
# Global variable to track call count
call_count = 0

async def process_file(file: UploadFile) -> str:
    logging.debug("Processing uploaded file...")
    # Process the uploaded file and return its content
    try:
        # Read and decode file content
        file_content = await file.read()
        return file_content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to process file")

@app.get("/")
def hello():
    return {"Hello" : "World"}

@app.post("/predict", response_model=Response)
async def predict(file: UploadFile = File(...), query: str = Body(...)) -> Any:
    global call_count
    call_count += 1
    logging.debug(f"Call #{call_count}: Generating response with file content and query.")
    
    # Check if the file type is supported
    allowed_extensions = {"docx", "pdf", "txt", "csv"}
    file_extension = file.filename.split(".")[-1]

    print(file_extension)
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Process uploaded file
    file_content = await process_file(file)

    # Generate response based on user query and file content
    try:
        response = generate_response(file_content, query)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate response")
    
    return {"result": response}



def generate_response(file_content: str, query: str) -> str:
    global call_count
    logging.debug(f"Generating response with file content and query:\n{file_content}\n{query}")
    
    try:
        if query:
            combined_text = f"File Content:\n{file_content}\nQuery: {query}"
        else:
            combined_text = file_content
        
        logging.debug(f"Combined text for generation:\n{combined_text}")

        # Generate response using nlp pipeline
        response = nlp(combined_text, max_length=1000, truncation=True, min_length=30, do_sample=False)[0]['generated_text']
        
        return response
    except Exception as err:
        logging.error(f"Error generating response: {err}")
        return f"Error generating response: {err}"







