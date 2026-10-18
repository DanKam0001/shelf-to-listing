# Snap Seller — submission copy

## Title
Snap Seller

## Tagline
One snap. Your listing's ready.

## Short description (one line)
Photograph anything you want to sell — get a ready-to-post marketplace listing back in seconds, written by a vision model running on AMD Instinct GPUs, with an honest confidence rating on the price.

## Long description
Writing a marketplace listing is the reason a pile of stuff never makes it online: finding the words, guessing a price, deciding what condition to call it. Take one photo of an item and a vision model returns a title, category, condition, a buyer-ready description, and a price with its reasoning — structured output, a few seconds, no market lookup pretending to be one (the app says so explicitly).

It rates its own confidence on that price (High/Medium/Low) and, when confidence isn't High, tells you exactly what to add — a brand label, a size tag, a measurement — to improve it. It's not guessing and hiding the guess; it's showing its work.

It's three use cases in one. Sellers clearing out a pile of stuff. Flippers doing rapid price-triage at an estate sale or thrift store — ten items, ten checks, before deciding what's worth buying. And people who genuinely don't know what the thing in their hands is: inherited junk, a garage-clean-out mystery item, point the camera and find out.

There's also a second feature: once a listing is generated, "Remove background" cuts the item out of the photo (transparent and plain-white versions, downloadable), since most marketplaces want a plain product shot, not a photo of your living room. (It works best on items that aren't being worn or held — the app says so up front.)

**Why AMD, specifically**: the honest case isn't "AMD is always cheaper" — published benchmarks are workload-dependent. But our workload is single-photo, one-at-a-time inference, not batched — and that's exactly the regime where AMD Instinct's larger memory per chip has shown a real per-token cost edge over the equivalent Nvidia setup (e.g. ~21% cheaper at batch size 1 in RunPod's published Mixtral 8x7B benchmark). For a flipper checking ten items instead of one, that's not a rounding error.

**Track:** Commerce — Reinvent Commerce
**Tech:** AMD Instinct GPUs (via Fireworks managed inference), Python, Streamlit, rembg (background removal)

## Tags
AMD, Commerce, Computer Vision, E-commerce, Fireworks AI, Python, Streamlit

## Narration script (demo video, ~65s)
See video/vo.json
