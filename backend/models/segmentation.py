import os
import io
import base64
import numpy as np
from PIL import Image
import httpx

HF_API_URL = "https://api-inference.huggingface.co/models/mattmdjaga/segformer_b2_clothes"

LABELS = {
    0: "Background", 1: "Hat", 2: "Hair", 3: "Sunglasses",
    4: "Upper-clothes", 5: "Skirt", 6: "Pants", 7: "Dress",
    8: "Belt", 9: "Left-shoe", 10: "Right-shoe", 11: "Face",
    12: "Left-leg", 13: "Right-leg", 14: "Left-arm", 15: "Right-arm",
    16: "Bag", 17: "Scarf",
}

CLOTHING_LABELS = {"Upper-clothes", "Skirt", "Pants", "Dress", "Belt", "Left-shoe", "Right-shoe"}


async def segment_clothing(image_bytes: bytes) -> bytes:
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        raise ValueError("HUGGINGFACE_API_TOKEN not set")

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        resp = await client.post(HF_API_URL, headers=headers, content=image_bytes, timeout=60.0)
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")

        if "application/json" in content_type:
            return _combine_clothing_masks(resp.json())
        else:
            return _fallback_mask(resp.content)


def _combine_clothing_masks(data: list) -> bytes:
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
