import os
import io
import numpy as np
from PIL import Image
from huggingface_hub import InferenceClient

CLOTHING_LABELS = {"Upper-clothes", "Skirt", "Pants", "Dress", "Belt", "Left-shoe", "Right-shoe"}


async def segment_clothing(image_bytes: bytes) -> bytes:
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        raise ValueError("HUGGINGFACE_API_TOKEN not set")

    client = InferenceClient(token=token)
    image = Image.open(io.BytesIO(image_bytes))

    try:
        result = client.image_segmentation(
            image,
            model="mattmdjaga/segformer_b2_clothes",
        )
    except Exception as e:
        raise RuntimeError(f"Hugging Face API call failed: {e}")

    masks = []
    for item in result:
        if item.label in CLOTHING_LABELS:
            masks.append(np.array(item.mask.convert("L")))

    if not masks:
        raise ValueError("No clothing detected in image")

    combined = np.maximum.reduce(masks).astype(np.uint8)
    combined[combined > 0] = 255

    result_img = Image.fromarray(combined, mode="L")
    buf = io.BytesIO()
    result_img.save(buf, format="PNG")
    return buf.getvalue()
