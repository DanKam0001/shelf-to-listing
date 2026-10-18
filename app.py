import streamlit as st
from PIL import Image

from listing import FALLBACK_MODEL, MODEL, generate_listing

st.set_page_config(page_title="Snap Seller", page_icon="📸", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

    :root {
        --bg: #FBF5EC;
        --panel: #FFFFFF;
        --ink: #241F1A;
        --mute: #6E6255;
        --accent: #C2551F;
        --accent-ink: #FFF6EE;
        --good: #2E6B4E;
        --warn: #B07A1E;
        --bad: #AE3B2B;
        --line: #E8DCC8;
    }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--ink); }
    .stApp { background: var(--bg); }
    h1, h2, h3 { font-family: 'Fraunces', serif !important; font-weight: 800 !important; color: var(--ink) !important; }
    p, span, label, div { color: var(--ink); }
    .stCaption, [data-testid="stCaptionContainer"] { color: var(--mute) !important; }

    .stButton button[kind="primary"] { background-color: var(--accent); color: var(--accent-ink); border: none; font-weight: 600; }
    .stButton button[kind="primary"]:hover { background-color: #A3461A; }
    .stButton button:not([kind="primary"]) { border-color: var(--line); color: var(--ink); }

    [data-testid="stFileUploader"] { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 4px; }
    [data-testid="stMetric"] { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 12px 16px; }
    [data-testid="stExpander"] { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; }

    .wordmark { font-family: 'Fraunces', serif; font-weight: 800; font-size: 42px; color: var(--ink); }
    .tagline { font-size: 18px; color: var(--mute); margin-top: -6px; }
    .howto { background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 22px 26px; }
    .howto li { margin-bottom: 8px; line-height: 1.5; }
    .pill { display: inline-block; font-weight: 700; font-size: 13px; letter-spacing: .3px; padding: 4px 12px; border-radius: 999px; }
    .pill-high { background: #E4F0E9; color: var(--good); }
    .pill-medium { background: #F6EBD6; color: var(--warn); }
    .pill-low { background: #F6DFDA; color: var(--bad); }
    .tipbox { background: #F6EBD6; border: 1px solid #E8D4A8; border-radius: 10px; padding: 14px 18px; margin-top: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="wordmark">📸 Snap Seller</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">One snap. Your listing\'s ready.</div>', unsafe_allow_html=True)
st.write("")

left, right = st.columns([1, 1.3], gap="large")

with left:
    st.markdown(
        """
        <div class="howto">
        <b>How it works</b>
        <ul>
        <li>Take or upload one clear photo of the item</li>
        <li>Click <b>Generate listing</b> — takes a few seconds</li>
        <li>Get a title, price, and description, plus a confidence rating on the price</li>
        <li>Low confidence? We'll tell you exactly what photo or detail would help</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    uploaded = st.file_uploader("Photo of the item", type=["jpg", "jpeg", "png"])

    if uploaded:
        if st.session_state.get("uploaded_id") != uploaded.file_id:
            st.session_state["uploaded_id"] = uploaded.file_id
            st.session_state.pop("result", None)
        st.image(uploaded, caption="Your photo", use_container_width=True)
        tmp_path = "uploaded_tmp.jpg"
        img = Image.open(uploaded).convert("RGB")
        img.thumbnail((1600, 1600))
        img.save(tmp_path, quality=90)

        if st.button("Generate listing", type="primary"):
            with st.spinner("Looking at the photo..."):
                try:
                    result = generate_listing(tmp_path, model=MODEL)
                except Exception:
                    try:
                        result = generate_listing(tmp_path, model=MODEL)  # one retry on the working model
                    except Exception:
                        result = generate_listing(tmp_path, model=FALLBACK_MODEL)
            st.session_state["result"] = result
    else:
        st.caption("Market stall items, garage-sale junk, a shop shelf — whatever you're trying to move.")

with right:
    result = st.session_state.get("result") if uploaded else None
    if result:
        st.subheader(result["title"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Price (AUD)", f"${result['suggested_price_aud']}")
        c2.metric("Category", result["category"])
        c3.metric("Condition", result["condition"])
        st.write(result["description"])

        conf = result.get("price_confidence", "Medium")
        pill_class = {"High": "pill-high", "Medium": "pill-medium", "Low": "pill-low"}.get(conf, "pill-medium")
        st.markdown(
            f'<span class="pill {pill_class}">PRICE CONFIDENCE: {conf.upper()}</span>',
            unsafe_allow_html=True,
        )
        st.caption(f"**How this price was estimated:** {result['price_reasoning']}")
        if result.get("confidence_reason"):
            st.caption(result["confidence_reason"])
        st.caption("This is general knowledge, not a live market lookup — no real listing was checked. Treat it as a starting point.")

        tips = result.get("improve_listing_tips") or []
        if tips:
            tip_html = "".join(f"<li>{t}</li>" for t in tips)
            st.markdown(
                f'<div class="tipbox"><b>Raise the confidence</b> — add one of these:<ul>{tip_html}</ul></div>',
                unsafe_allow_html=True,
            )

        st.divider()
        with st.expander("What the model actually returned"):
            st.json(result)
    elif uploaded:
        st.caption("Click **Generate listing** on the left to see your results here.")
    else:
        st.caption("Your listing will appear here once you upload a photo and generate it.")
