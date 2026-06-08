import os
import io
import asyncio
import logging
import numpy as np
from PIL import Image
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)

CLOTHING_LABELS = {"Upper-clothes", "Skirt", "Pants", "Dress", "Belt", "Left-shoe", "Right-shoe"}


async def segment_clothing(image_bytes: bytes) -> bytes:
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        raise ValueError("HUGGINGFACE_API_TOKEN not set")

    client = InferenceClient(token=token)

    def _call():
        return client.image_segmentation(
            image=image_bytes,
            model="mattmdjaga/segformer_b2_clothes",
        )

    logger.info("Sending request to Hugging Face Inference API...")
    result = await asyncio.to_thread(_call)
    logger.info(f"Received {len(result)} segments from API")

    masks = []
    for item in result:
        label = item["label"]
        if label in CLOTHING_LABELS:
            mask_img = item["mask"].convert("L")
            masks.append(np.array(mask_img))

    if not masks:
        raise ValueError("No clothing detected in image")

    combined = np.maximum.reduce(masks).astype(np.uint8)
    combined[combined > 0] = 255

    result_img = Image.fromarray(combined, mode="L")
    buf = io.BytesIO()
    result_img.save(buf, format="PNG")
    return buf.getvalue()
