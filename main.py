from fastapi import FastAPI, UploadFile, File, Header, Query
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

def resolve_lang(lang_param: str | None, accept_language: str | None) -> str:
    cand = (lang_param or (accept_language or "en")).split(",")[0].split("-")[0].lower()
    return "he" if cand.startswith("he") else "en"

def build_prompt(target_lang: str) -> str:
    # We keep the same shape but ask the model to localize user-visible fields.
    # Also ask for English mirrors so we can optionally store/search canonically.
    return (
        "You help catalog items for a rental marketplace.\n"
        "Analyze the image and return STRICT JSON only (no prose, no code fences).\n\n"
        "Required keys (always present):\n"
        "- title (string)\n"
        "- brand (string or null)\n"
        "- description (string)\n"
        "- condition (one of: Brand new, Used - like new, Used - good, Used - fair)\n"
        "- category (one of: sport, electronics, tools, home, garden, camping, pets, party, furniture, fashion, costumes, other)\n"
        "- tags (array of short keywords)\n\n"
        "Also include English mirrors for search/storage:\n"
        "- title_en, description_en, tags_en (array)\n\n"
        "Language rule:\n"
        f"- Produce user-visible fields in TARGET LANGUAGE = '{'Hebrew' if target_lang=='he' else 'English'}'.\n"
        "- Keep brand names, model numbers and units (e.g., 18V, 4K) as-is.\n"
        "- Be concise and marketplace-style.\n\n"
        "Validation:\n"
        "- Respond with ONE JSON object only. No markdown, no commentary.\n"
    )

@app.post("/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    lang: str = Query("en"),
    accept_language: str | None = Header(None),
):
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

    target_lang = resolve_lang(lang, accept_language)
    prompt = build_prompt(target_lang)

    try:
        print(f"📡 Sending request to OpenAI (target_lang={target_lang})...")
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
            max_tokens=600
        )

        result = response.choices[0].message.content or ""
        print("🧾 Raw OpenAI response:", result[:600])

        # Strip possible code fences while allowing pure JSON
        cleaned = re.sub(r"^```(?:json)?|```$", "", result.strip(), flags=re.IGNORECASE).strip("` \n")

        parsed = json.loads(cleaned)

        # Ensure we always return the locale so the UI knows what it got
        parsed["locale"] = target_lang

        # Soft guard: If model forgot to mirror English, add fallbacks
        if "title_en" not in parsed and "title" in parsed:
            parsed["title_en"] = parsed["title"]
        if "description_en" not in parsed and "description" in parsed:
            parsed["description_en"] = parsed["description"]
        if "tags_en" not in parsed and "tags" in parsed and isinstance(parsed["tags"], list):
            parsed["tags_en"] = parsed["tags"]

        return JSONResponse(content=parsed)

    except json.JSONDecodeError:
        print("❌ Failed to parse OpenAI JSON")
        return JSONResponse(content={"error": "Invalid JSON", "raw": result}, status_code=500)

    except Exception as e:
        print("❌ Exception during OpenAI call:")
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)
