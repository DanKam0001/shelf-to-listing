# 📸 Snap Seller

One snap. Your listing's ready.

Take a photo of anything you want to sell — a market-stall find, a garage-sale
piece, something sitting on a shop shelf — and a vision-language model looks
at it directly and writes the listing: title, category, condition, a
buyer-ready description, and a suggested price with its reasoning, plus a
confidence rating on that price and concrete tips to raise it. No typing,
no guessing what to charge.

Built for **AMD Developer Hackathon: ACT III** — Commerce track.

## How it works

One photo goes to a vision-capable open model served by
[Fireworks AI](https://fireworks.ai), whose managed inference runs on **AMD
Instinct GPUs**. The model returns structured JSON in one call — no
multi-step pipeline, no separate pricing lookup, no OCR step. See
[`listing.py`](listing.py).

## Run it

```bash
python -m venv venv
venv\Scripts\activate          # or source venv/bin/activate on macOS/Linux
pip install -r requirements.txt
```

Create a `.env` file:

```
FIREWORKS_API_KEY=your_key_here
FIREWORKS_BASE_URL=https://api.fireworks.ai/inference/v1
```

Then:

```bash
streamlit run app.py
```

Or from the CLI:

```bash
python listing.py path/to/photo.jpg
```

## Also: clean up the photo

After generating a listing, "Remove background" cuts the item out of the photo (transparent and
plain-white versions, downloadable as PNG) via a local segmentation model (`rembg`/u2net) — most
marketplaces want a plain-background product shot, not your actual room.

That automatic mode isolates whatever's most visually prominent, which is the *person* when the
item is being worn or held. For that case, "Item worn or held by someone? Click on it instead"
lets you click directly on the item in the photo (one or more points) and runs point-prompted
segmentation (FastSAM) from those exact clicks — it cuts out the material you pointed at, not
whatever looks most salient.

## Demo

See `video/demo.mp4` for a recording of the real app generating listings from
two real photos, live, with no edits to the output.

## Tech

- **AMD Instinct GPUs** via Fireworks' managed, OpenAI-compatible inference API
- Python, Streamlit
- A single vision-language model call per listing — `glm-5p3-flash`, with
  `kimi-k3-fast` as an automatic fallback

## Demo video photo credits

The two photos used in `video/demo.mp4` are real, unstaged photos from Wikimedia Commons
(not stock photography, not AI-generated):

- Yard sale items: [BoiseYardSaleSwag.jpg](https://commons.wikimedia.org/wiki/File:BoiseYardSaleSwag.jpg)
  by Kencf0618, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- Crockery lot: [ALANG SECOND SALE MARKET 6.jpg](https://commons.wikimedia.org/wiki/File:ALANG_SECOND_SALE_MARKET_6.jpg)
  by Bambhaniya Ravikumar, [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)

## Track rule compliance

This is not a demand/sales forecasting tool, so the Commerce track's
"LLM can't be the sole forecasting method" rule doesn't apply — there's no
forecasting here, just description and price estimation from a single photo.
