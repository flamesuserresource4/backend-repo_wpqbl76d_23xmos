from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="VisionFlow AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextVideoRequest(BaseModel):
    prompt: str = Field(..., min_length=3)
    duration_seconds: int = Field(..., ge=1, le=60, description="Demo limit: up to 60s")
    voiceover: Optional[str] = None


DEMO_VIDEO_URL = "https://cdn.coverr.co/videos/coverr-black-cat-1447/1080p.mp4"


@app.post("/api/generate-text-video")
async def generate_text_video(req: TextVideoRequest):
    prompt = req.prompt.strip()
    blocked = any(w in prompt.lower() for w in ["nsfw", "nude", "sexual"])  # very basic moderation demo
    if blocked:
        raise HTTPException(status_code=400, detail="Prompt blocked by moderation policy.")

    # Demo: Return a static video. Replace with real provider integration for prompt fidelity.
    return {"url": DEMO_VIDEO_URL, "note": "Demo mode: static sample video returned."}


@app.post("/api/generate-image-video")
async def generate_image_video(image: UploadFile = File(...), duration_seconds: int = 60):
    if duration_seconds > 60:
        raise HTTPException(status_code=400, detail="Demo allows up to 60 seconds only.")

    content_type = image.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload a valid image file.")

    # Demo: Return a static video regardless of input image.
    return {"url": DEMO_VIDEO_URL, "note": "Demo mode: static sample video returned."}


@app.get("/test")
async def test():
    return {"status": "ok"}
