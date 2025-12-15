import streamlit as st

from utils.pixel import (
    get_pixelbin_client,
    upload_to_pixelbin,
    build_transform_url,
    download_image
)
from utils.helpers import init_results_state, create_zip


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Watermark Remover",
    page_icon="favicon.ico"
)

st.title("Propkee - Watermark Remover")

# ---------------- API KEY INPUT ----------------
api_key = st.text_input(
    "Enter your API Key",
    type="password"
)

if not api_key:
    st.info("Please enter your API key to continue.")
    st.stop()

client = get_pixelbin_client(api_key)

# ---------------- UI ----------------
uploaded_files = st.file_uploader(
    "Upload image(s)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

init_results_state(st)

if uploaded_files and st.button("🧽 Remove Watermarks"):
    st.session_state.results.clear()
    progress = st.progress(0)

    for i, file in enumerate(uploaded_files, 1):
        with st.spinner(f"Processing {file.name} ({i}/{len(uploaded_files)})"):
            try:
                pixelbin_url = upload_to_pixelbin(client, file)
                transformed_url = build_transform_url(pixelbin_url)
                cleaned = download_image(transformed_url)

                st.session_state.results.append({
                    "name": file.name,
                    "original": file,
                    "cleaned": cleaned
                })
            except Exception as e:
                st.error(f"❌ {file.name}: {e}")

        progress.progress(i / len(uploaded_files))

# ---------------- RESULTS ----------------
if st.session_state.results:
    st.subheader("✅ Cleaned Images")

    for idx, img in enumerate(st.session_state.results, 1):
        col1, col2 = st.columns(2)

        with col1:
            st.image(img["original"], caption="Original", width="stretch")

        with col2:
            st.image(img["cleaned"], caption="Cleaned", width="stretch")
            st.download_button(
                "⬇️ Download Image",
                img["cleaned"],
                file_name=f"cleaned_{idx}.png",
                mime="image/png",
                key=f"download_{idx}"
            )

    zip_buffer = create_zip(st.session_state.results)
    st.download_button(
        "📦 Download All as ZIP",
        zip_buffer,
        file_name="cleaned_images.zip",
        mime="application/zip"
    )
