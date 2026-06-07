from fastapi import APIRouter, UploadFile, File, Form
from models.inpainting import inpaint_image
from models.segmentation import segment_clothing

router = APIRouter(prefix="/api")


@router.post("/upload")
async def upload_photo(file: UploadFile = File(...)):
    return {"filename": file.filename, "size": len(await file.read())}


@router.post("/edit")
async def edit_photo(
    file: UploadFile = File(...),
    prompt: str = Form(...),
):
    mask = await segment_clothing(file)
    result = await inpaint_image(file, mask, prompt)
    return {"result": result}
