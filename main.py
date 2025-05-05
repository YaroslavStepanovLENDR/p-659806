from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "✅ LENDR GPT-4 Vision API is live!"}

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    if file is None:
        return JSONResponse(content={"error": "No file received"}, status_code=400)

    contents = await file.read()

    files = {
        "file": (file.filename, contents, "image/jpeg")
    }

    try:
        # Replace with actual model or processing
        result = {
            "title": "Mountain Bike",
            "brand": "Giant",
            "description": "A blue aluminum mountain bike with 21 speeds.",
            "condition": "Used - good",
            "category": "Sport",
            "tags": ["bike", "mountain", "gear"]
        }

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
