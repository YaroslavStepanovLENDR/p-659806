
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import json

app = FastAPI()

# Enable CORS
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
    try:
        # Read file contents
        file_contents = await file.read()
        
        # Create form data with the file
        files = {'file': (file.filename, file_contents, file.content_type)}
        
        # Make request to the new endpoint
        response = requests.post(
            'https://lendr-backend.onrender.com/analyze-image',
            files=files
        )
        
        # Parse the response
        data = response.json()
        
        # If we got raw JSON string, try to parse it
        if 'raw' in data:
            try:
                # Try to parse the raw string as JSON
                parsed_data = json.loads(data['raw'])
                return JSONResponse(content=parsed_data)
            except json.JSONDecodeError:
                # If parsing fails, return the raw response
                return JSONResponse(content=data)
        
        # If we already have parsed JSON, return it directly
        return JSONResponse(content=data)
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to process image"},
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000)
