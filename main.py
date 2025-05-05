from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import openai
import base64
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load OpenAI API key from environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    if file is None:
        return JSONResponse(content={"error": "No file received"}, status_code=400)

    contents = await file.read()
    b64_image = base64.b64encode(contents).decode("utf-8")

    prompt = (
        "You are helping someone catalog items for renting. "
        "Please analyze the image and return a JSON with:\n"
        "- title (string)\n"
        "- brand (string or null)\n"
        "- description (string)\n"
        "- condition: one of [Brand new, Used - like new, Used - good, Used - fair]\n"
        "- category: one of [sport, electronics, tools, home, garden, camping, pets, party, furniture, fashion, costumes, other]\n"
        "- tags: array of keywords\n\n"
        "Respond only with a JSON object, no extra text."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                    ]
                }
            ],
            max_tokens=500
        )
        result = response.choices[0].message.content
        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
