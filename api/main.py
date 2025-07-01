from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "OCR Gateway API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)