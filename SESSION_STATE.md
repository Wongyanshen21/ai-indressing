# AI Indressing — Session State

## Project
AI-powered virtual outfit try-on. Upload a photo, AI segments clothing and inpaints new outfits based on prompts.

## What's Working
- FastAPI backend running on Render (`https://ai-indressing-api.onrender.com`)
- Clothing segmentation via Hugging Face SegFormer (`POST /api/segment`)
- File upload, health check, HF connectivity test endpoints
- Dockerfile for backend deployment
- Next.js 14 frontend scaffold with routing
- Shared prompt templates for clothing/hair

## What's Stubs / TODO
- **Inpainting** (`backend/models/inpainting.py`) — placeholder, needs FLUX.1 Fill implementation
- **Photo Editor** component — placeholder
- **Character Wizard** — placeholder
- **All frontend pages** — just placeholder text, no API integration
- **No database, no auth**
- **`requests`** no longer used anywhere — can be removed from requirements.txt

## Bugs Fixed This Session
- **DNS resolution failure** — `api-inference.huggingface.co` is **deprecated** and no longer exists in DNS. Switched to `huggingface_hub` `InferenceClient` which routes through the correct provider endpoint (`router.huggingface.co`).
- **`backend/models/segmentation.py`** — Rewritten to use `huggingface_hub.InferenceClient.image_segmentation()` instead of raw `requests.post()` to the dead URL.
- **`backend/api/routes.py`** — `/hf-test` now uses `HfApi.whoami()` to verify the token. Removed `requests` import. Added `/dns-test` diagnostic endpoint.

## Render Issue (Resolved)
The root cause was that `api-inference.huggingface.co` is a **dead DNS record**. The `huggingface_hub` library routes through `router.huggingface.co` which resolves correctly. No special Render DNS configuration needed.

## Next Steps
1. Push code → Render auto-deploys → test `/api/hf-test` and `/api/segment`
2. Implement inpainting in `models/inpainting.py`
3. Build frontend components (PhotoEditor, CharacterWizard)
4. Wire frontend to backend API
5. Create `render.yaml` for full deployment config

## Render Config
- Service URL: `https://ai-indressing-api.onrender.com`
- Dockerfile path: `backend/Dockerfile`
- Root Directory: set to `backend/` on Render
- Env vars needed: `HUGGINGFACE_API_TOKEN`
