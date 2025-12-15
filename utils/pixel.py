import os
import io
import time
import tempfile
import asyncio
import requests
from pixelbin import PixelbinClient, PixelbinConfig
from pixelbin.utils.url import url_to_obj, obj_to_url

# ---------------- FIX EVENT LOOP ----------------
def ensure_event_loop():
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

# ---------------- CLIENT FACTORY ----------------
def get_pixelbin_client(api_key: str) -> PixelbinClient:
    ensure_event_loop()

    config = PixelbinConfig({
        "domain": "https://api.pixelbin.io",
        "apiSecret": api_key
    })
    return PixelbinClient(config=config)

# ---------------- PIXELBIN HELPERS ----------------
def upload_to_pixelbin(client: PixelbinClient, file):
    suffix = "." + file.name.split(".")[-1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.getvalue())
        tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        result = client.uploader.upload(
            file=f,
            name=file.name,
            path="",
            access="public-read",
            overwrite=True
        )

    os.remove(tmp_path)
    return result["url"]

def build_transform_url(asset_url: str) -> str:
    obj = url_to_obj(asset_url)
    obj["transformations"] = [
        {
            "plugin": "wm",
            "name": "remove",
            "values": [
                {"key": "rem_text", "value": "true"},
                {"key": "rem_logo", "value": "true"}
            ]
        },
        {
            "plugin": "t",
            "name": "toFormat",
            "values": [{"key": "f", "value": "png"}]
        }
    ]
    return obj_to_url(obj)

def download_image(url: str) -> io.BytesIO:
    for _ in range(12):
        r = requests.get(url, stream=True)
        if r.status_code == 202:
            time.sleep(1)
            continue
        r.raise_for_status()
        return io.BytesIO(r.content)

    raise RuntimeError("Processing timed out")
