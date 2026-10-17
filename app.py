import streamlit as st
from PIL import Image

from listing import FALLBACK_MODEL, MODEL, generate_listing

st.set_page_config(page_title="Shelf to Listing", page_icon="🏷️", layout="centered")
st.title("🏷️ Shelf to Listing")
st.caption("Photo in, ready-to-post marketplace listing out. Vision inference runs on AMD Instinct GPUs via Fireworks.")

uploaded = st.file_uploader("Take or upload a photo of the item", type=["jpg", "jpeg", "png"])

if uploaded:
    st.image(uploaded, caption="Your photo", use_container_width=True)
    tmp_path = "uploaded_tmp.jpg"
    Image.open(uploaded).convert("RGB").save(tmp_path)

    if st.button("Generate listing", type="primary"):
        with st.spinner("Looking at the photo and writing your listing..."):
            try:
                result = generate_listing(tmp_path, model=MODEL)
            except Exception:
                result = generate_listing(tmp_path, model=FALLBACK_MODEL)

        st.success("Listing ready")
        st.subheader(result["title"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Price (AUD)", f"${result['suggested_price_aud']}")
        c2.metric("Category", result["category"])
        c3.metric("Condition", result["condition"])
        st.write(result["description"])
        st.caption(f"Price reasoning: {result['price_reasoning']}")
        st.divider()
        with st.expander("Raw JSON (for devs / proof of structured output)"):
            st.json(result)
else:
    st.info("Upload a photo to get started — market stall items, garage-sale junk, a shop shelf, anything.")
