from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import openai
import base64
import os
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
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise Exception("OPENAI_API_KEY is missing from environment variables")

    openai.api_key = OPENAI_API_KEY

    contents = await file.read()
    base64_image = base64.b64encode(contents).decode("utf-8")

    response = openai.chat.completions.create(
        model="gpt-4-turbo-2024-04-09",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You're helping list an item on a peer-to-peer rental app. "
                            "Please analyze the image and provide the following in JSON:\n"
                            "- title (short, clear)\n"
                            "- brand (if visible)\n"
                            "- description (brief but helpful)\n"
                            "- condition (Brand new, Used - like new, Used - good, Used - fair)\n"
                            "- category (one of: sport, electronics, tools, home, garden, camping, pets, party, furniture, fashion, costumes, other)\n"
                            "- tags (list of 3–6 relevant words)"
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=500
    )

    import re

    result = response.choices[0].message.content.strip()

    # Remove triple backticks if present
    if result.startswith("```"):
        result = re.sub(r"^```(?:json)?|```$", "", result, flags=re.MULTILINE).strip()

    print("🧠 GPT-4 Response:\n", result)

    try:
        parsed = json.loads(result)
        return JSONResponse(content=parsed)
    except:
        return JSONResponse(content={"raw": result})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000)
