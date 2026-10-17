import io

import streamlit as st
from PIL import Image

from isolate import isolate_item, isolate_on_white
from listing import FALLBACK_MODEL, MODEL, generate_listing

st.set_page_config(page_title="Shelf to Listing", page_icon="🏷️", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700&family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Fraunces', serif !important; font-weight: 700 !important; }
    .stButton button[kind="primary"] { background-color: #1a1a1a; border: none; }
    .stButton button[kind="primary"]:hover { background-color: #333; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Shelf to Listing")
st.caption("Upload a photo of something you're selling. It writes the listing.")

uploaded = st.file_uploader("Photo of the item", type=["jpg", "jpeg", "png"])

if uploaded:
    if st.session_state.get("uploaded_id") != uploaded.file_id:
        st.session_state["uploaded_id"] = uploaded.file_id
        st.session_state.pop("result", None)
        st.session_state.pop("cutout", None)
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
        st.session_state.pop("cutout", None)  # a new listing means a stale cutout, if any

    result = st.session_state.get("result")
    if result:
        st.subheader(result["title"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Price (AUD)", f"${result['suggested_price_aud']}")
        c2.metric("Category", result["category"])
        c3.metric("Condition", result["condition"])
        st.write(result["description"])
        st.caption(result["price_reasoning"])
        st.caption("Single photo, no market lookup. Treat the price as a starting point, not a quote.")
        st.divider()

        with st.expander("What the model actually returned"):
            st.json(result)

        st.divider()
        st.subheader("Clean up the photo")
        st.caption("Cuts the item out so you're not posting a photo of your living room.")
        if st.button("Remove background"):
            with st.spinner("Isolating the item..."):
                st.session_state["cutout"] = isolate_item(tmp_path)
                st.session_state["on_white"] = isolate_on_white(tmp_path)

        if "cutout" in st.session_state:
            c1, c2 = st.columns(2)
            c1.image(st.session_state["cutout"], caption="Transparent background")
            c2.image(st.session_state["on_white"], caption="On plain white")
            buf = io.BytesIO()
            st.session_state["cutout"].save(buf, format="PNG")
            st.download_button("Download cutout (PNG)", buf.getvalue(), file_name="item_cutout.png", mime="image/png")
else:
    st.caption("Market stall items, garage-sale junk, a shop shelf — whatever you're trying to move.")
