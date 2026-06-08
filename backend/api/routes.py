import os
import json
import socket
import asyncio
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from models.segmentation import segment_clothing
from models.inpainting import inpaint_image

router = APIRouter(prefix="/api")


@router.get("/dns-test")
async def test_dns():
    hosts = [
        "api-inference.huggingface.co",
        "huggingface.co",
        "google.com",
    ]
    results = {}
    for host in hosts:
        try:
            ip = socket.gethostbyname(host)
            results[host] = {"ip": ip, "status": "ok"}
        except OSError as e:
            results[host] = {"error": str(e), "status": "failed"}
    return results


@router.get("/presets")
async def get_presets():
    presets_path = Path(__file__).resolve().parent.parent / "presets.json"
    if not presets_path.exists():
        return {"presets": []}
    return json.loads(presets_path.read_text(encoding="utf-8"))


@router.post("/upload")
async def upload_photo(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents)}


@router.get("/hf-test")
async def test_hf_connectivity():
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        return {"error": "HUGGINGFACE_API_TOKEN not set"}

    try:
        from huggingface_hub import HfApi
        api = HfApi(token=token)

        def _test():
            return api.whoami()

        identity = await asyncio.to_thread(_test)
        return {
            "status": "ok",
            "user": identity.get("name", identity.get("email", "unknown")),
        }
    except Exception as e:
        return {"error": str(e), "message": "Hugging Face API test failed"}


@router.post("/segment")
async def get_clothing_mask(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        mask_bytes = await segment_clothing(contents)
        return Response(content=mask_bytes, media_type="image/png")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Segmentation API error: {str(e)}")


@router.post("/inpaint")
async def inpaint(file: UploadFile = File(...), mask: UploadFile = File(...), prompt: str = Form("")):
    image_bytes = await file.read()
    mask_bytes = await mask.read()
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")
    try:
        result_bytes = await inpaint_image(image_bytes, mask_bytes, prompt)
        return Response(content=result_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Inpainting error: {str(e)}")
