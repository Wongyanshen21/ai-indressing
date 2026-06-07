import os
import requests
import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from models.segmentation import segment_clothing

router = APIRouter(prefix="/api")


@router.post("/upload")
async def upload_photo(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents)}


@router.get("/hf-test")
async def test_hf_connectivity():
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        return {"error": "HUGGINGFACE_API_TOKEN not set"}

    def _test():
        return requests.get(
            "https://api-inference.huggingface.co/models/mattmdjaga/segformer_b2_clothes",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )

    try:
        resp = await asyncio.to_thread(_test)
        return {
            "status_code": resp.status_code,
            "body_preview": resp.text[:300],
        }
    except Exception as e:
        return {"error": str(e)}


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
