from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from models.segmentation import segment_clothing

router = APIRouter(prefix="/api")


@router.post("/upload")
async def upload_photo(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents)}


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
