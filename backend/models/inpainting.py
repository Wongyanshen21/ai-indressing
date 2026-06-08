import io
import asyncio
import logging
from PIL import Image

logger = logging.getLogger(__name__)


async def inpaint_image(image_bytes: bytes, mask_bytes: bytes, prompt: str) -> bytes:
    logger.info(f"Inpainting with prompt: {prompt[:50]}...")

    def _process():
        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        mask = Image.open(io.BytesIO(mask_bytes)).convert("L")

        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        overlay.paste((255, 0, 0, 80), mask=mask)
        result = Image.alpha_composite(img, overlay).convert("RGB")

        buf = io.BytesIO()
        result.save(buf, format="PNG")
        return buf.getvalue()

    return await asyncio.to_thread(_process)
