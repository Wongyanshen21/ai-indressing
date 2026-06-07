import os
import io
import base64
import logging
import asyncio
import requests
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

HF_API_URL = "https://api-inference.huggingface.co/models/mattmdjaga/segformer_b2_clothes"
CLOTHING_LABELS = {"Upper-clothes", "Skirt", "Pants", "Dress", "Belt", "Left-shoe", "Right-shoe"}


async def segment_clothing(image_bytes: bytes) -> bytes:
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        raise ValueError("HUGGINGFACE_API_TOKEN not set")

    headers = {"Authorization": f"Bearer {token}"}

    def _call_hf():
        return requests.post(HF_API_URL, headers=headers, data=image_bytes, timeout=120)

    logger.info("Sending request to HF API...")
    resp = await asyncio.to_thread(_call_hf)
    logger.info(f"HF API responded with status {resp.status_code}")

    if resp.status_code == 503:
        logger.info("Model is loading, retrying once...")
        await asyncio.sleep(5)
        resp = await asyncio.to_thread(_call_hf)
        logger.info(f"HF API retry responded with status {resp.status_code}")

    if resp.status_code != 200:
        raise RuntimeError(f"HF API returned {resp.status_code}: {resp.text[:500]}")

    content_type = resp.headers.get("content-type", "")

    if "application/json" in content_type:
        data = resp.json()
        if isinstance(data, dict) and "error" in data:
            raise RuntimeError(f"HF API error: {data['error']}")
        return _parse_json_response(data)
    else:
        return _fallback_mask(resp.content)


def _parse_json_response(data: list) -> bytes:
    masks = []
    for item in data:
        label = item.get("label", "")
        if label in CLOTHING_LABELS:
            mask_bytes = base64.b64decode(item["mask"])
            mask_img = Image.open(io.BytesIO(mask_bytes)).convert("L")
            masks.append(np.array(mask_img))

    if not masks:
        raise ValueError("No clothing detected in image")

    combined = np.maximum.reduce(masks).astype(np.uint8)
    combined[combined > 0] = 255

    result = Image.fromarray(combined, mode="L")
    buf = io.BytesIO()
    result.save(buf, format="PNG")
    return buf.getvalue()


def _fallback_mask(image_bytes: bytes) -> bytes:
    mask_img = Image.open(io.BytesIO(image_bytes)).convert("L")
    mask_img = mask_img.point(lambda x: 255 if x > 0 else 0)
    buf = io.BytesIO()
    mask_img.save(buf, format="PNG")
    return buf.getvalue()
