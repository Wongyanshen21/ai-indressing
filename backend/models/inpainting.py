import os
import io
import asyncio
import logging
from PIL import Image
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)


async def inpaint_image(image_bytes: bytes, mask_bytes: bytes, prompt: str) -> bytes:
    logger.info(f"Inpainting with prompt: {prompt[:50]}...")

    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        raise ValueError("HUGGINGFACE_API_TOKEN not set")

    client = InferenceClient(token=token, provider="fal-ai")

    def _call():
        return client.image_to_image(
            image=image_bytes,
            prompt=prompt,
            model="black-forest-labs/FLUX.1-Kontext-dev",
        )

    result_img = await asyncio.to_thread(_call)
    result_img = result_img.convert("RGB")

    original = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    mask = Image.open(io.BytesIO(mask_bytes)).convert("L")

    result_img = result_img.resize(original.size)
    mask = mask.resize(original.size)

    final = Image.composite(result_img, original, mask)

    buf = io.BytesIO()
    final.save(buf, format="PNG")
    return buf.getvalue()
