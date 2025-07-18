from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import base64, os, traceback, json, re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return JSONResponse(content={"status": "Backend running test"}, status_code=200)

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    print("✅ /analyze-image endpoint hit")

    if file is None:
        print("❌ No file received")
        return JSONResponse(content={"error": "No file received"}, status_code=400)

    try:
        contents = await file.read()
        print(f"📷 File read successfully, size: {len(contents)} bytes")
        b64_image = base64.b64encode(contents).decode("utf-8")
    except Exception as file_err:
        print("❌ Error reading file:", file_err)
        return JSONResponse(content={"error": "Failed to read uploaded file"}, status_code=500)

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
        print("📡 Sending request to OpenAI...")
        response = client.chat.completions.create(
            model="gpt-4o",
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
        print("🧾 Raw OpenAI response:", result)

        # Strip Markdown-style code block
        cleaned = re.sub(r"^```(?:json)?|```$", "", result.strip(), flags=re.IGNORECASE).strip("` \n")

        parsed = json.loads(cleaned)
        return JSONResponse(content=parsed)

    except json.JSONDecodeError:
        print("❌ Failed to parse OpenAI JSON")
        return JSONResponse(content={"error": "Invalid JSON", "raw": result}, status_code=500)

    except Exception as e:
        print("❌ Exception during OpenAI call:")
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)
