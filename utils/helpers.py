import io
import zipfile

def init_results_state(st):
    if "results" not in st.session_state:
        st.session_state.results = []

def create_zip(results) -> io.BytesIO:
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for idx, img in enumerate(results, 1):
            zipf.writestr(
                f"cleaned_{idx}.png",
                img["cleaned"].getvalue()
            )

    zip_buffer.seek(0)
    return zip_buffer
