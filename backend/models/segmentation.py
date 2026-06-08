import io
import logging
import numpy as np
from PIL import Image
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation

logger = logging.getLogger(__name__)

CLOTHING_LABELS = {"Upper-clothes", "Skirt", "Pants", "Dress", "Belt", "Left-shoe", "Right-shoe"}

_model = None
_processor = None


def _ensure_model():
    global _model, _processor
    if _model is None:
        logger.info("Loading segmentation model (this may take a minute on first request)...")
        model_id = "mattmdjaga/segformer_b2_clothes"
        _processor = SegformerImageProcessor.from_pretrained(model_id)
        _model = SegformerForSemanticSegmentation.from_pretrained(model_id)
        logger.info("Segmentation model loaded")
    return _model, _processor


async def segment_clothing(image_bytes: bytes) -> bytes:
    model, processor = _ensure_model()

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    preds = outputs.logits.argmax(dim=1).squeeze().cpu().numpy().astype(np.uint8)

    id2label = model.config.id2label

    clothing_mask = np.zeros_like(preds, dtype=np.uint8)
    for class_id, label in id2label.items():
        if label in CLOTHING_LABELS:
            clothing_mask = np.maximum(clothing_mask, (preds == class_id).astype(np.uint8))

    if clothing_mask.sum() == 0:
        raise ValueError("No clothing detected in image")

    clothing_mask[clothing_mask > 0] = 255
    mask_img = Image.fromarray(clothing_mask, mode="L")

    mask_img = mask_img.resize(image.size, Image.NEAREST)

    buf = io.BytesIO()
    mask_img.save(buf, format="PNG")
    return buf.getvalue()
