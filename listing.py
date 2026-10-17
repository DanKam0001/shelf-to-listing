"""Core: one photo in, one e-commerce listing out, via a vision model on Fireworks (AMD Instinct GPUs)."""
import base64
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = "accounts/fireworks/models/glm-5p3-flash"
FALLBACK_MODEL = "accounts/fireworks/routers/kimi-k3-fast"

_client = OpenAI(
    api_key=os.environ["FIREWORKS_API_KEY"],
    base_url=os.environ.get("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1"),
)

PROMPT = """You are helping a small seller turn a photo into an online marketplace listing.
Look at the photo and identify the single most prominent item for sale (if several items are visible, pick the clearest one).

Return ONLY a JSON object, no other text, with exactly these keys:
{
  "title": "short punchy listing title, under 70 characters",
  "category": "one or two word product category",
  "condition": "New / Like New / Good / Fair, your best guess from the photo",
  "description": "2-3 sentence listing description a buyer would read, written in plain friendly language",
  "suggested_price_aud": "a realistic single AUD price guess as a number, your best estimate for a used/private-sale item of this kind",
  "price_reasoning": "one short sentence explaining the price guess"
}
"""


def _image_data_uri(path: str) -> str:
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = path.rsplit(".", 1)[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64,{b64}"


def generate_listing(image_path: str, model: str = MODEL) -> dict:
    data_uri = _image_data_uri(image_path)
    resp = _client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ],
            }
        ],
        max_tokens=500,
        temperature=0.4,
    )
    text = resp.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "test.jpg"
    try:
        result = generate_listing(path)
    except Exception as e:
        print(f"primary model failed ({e}), trying fallback...")
        result = generate_listing(path, model=FALLBACK_MODEL)
    print(json.dumps(result, indent=2))
