from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from aws import *
import os
import requests
import uvicorn
import logging
import json

app = FastAPI()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "OCR Gateway API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/ocr/text")
async def oct_text(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # 고유한 파일 이름 생성
    generated_file_name = generate_log_filename(file.filename)
    s3_url = await upload_and_get_s3_url(file, generated_file_name)


    payload = {
    "s3_url": s3_url
    }

    alb_url = os.environ["AWS_ALB_URL"]

    response = requests.post(alb_url, json=payload)
    response_data = response.json()

    await save_json_data(response_data, generated_file_name)
        
    return JSONResponse(content=response_data)

async def save_json_data(data: dict, generated_file_name: str):
    """Save given JSON data to local file using the base name of the generated file"""

    base_name = os.path.splitext(generated_file_name)[0]
    filename = f"{base_name}.json"
    filepath = f"./log/{filename}"

    
    # 파일 저장
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    

    return {"message": "JSON data saved successfully", "filename": filename}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)