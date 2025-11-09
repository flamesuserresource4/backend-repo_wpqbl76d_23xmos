import os
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="VisionFlow AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        # Try to import database module
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# -----------------------------
# VisionFlow AI minimal API
# -----------------------------

SAFE_MAX_SECONDS = 60  # Demo limit to control costs

NSFW_KEYWORDS = {
    "explicit", "nsfw", "nudity", "gore", "violence", "blood", "sexual",
}


def moderate_prompt(prompt: str):
    p = (prompt or "").lower()
    for word in NSFW_KEYWORDS:
        if word in p:
            raise HTTPException(status_code=400, detail="Prompt blocked by moderation policy.")


class TextVideoRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt to guide video generation")
    duration_seconds: int = Field(30, ge=1, le=3600)


class GenerateResponse(BaseModel):
    url: str
    provider: str = "demo"
    duration_seconds: int
    note: Optional[str] = None


@app.post("/api/generate-text-video", response_model=GenerateResponse)
async def generate_text_video(payload: TextVideoRequest):
    # Moderation & limits
    moderate_prompt(payload.prompt)
    if payload.duration_seconds > SAFE_MAX_SECONDS:
        raise HTTPException(status_code=400, detail="Demo limit: max 60 seconds")

    # In a real integration, call Replicate/Runway/Pika here and return the video URL.
    # For this sandbox, return a stable sample video URL so the UI can function end-to-end.
    sample_url = "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"

    return GenerateResponse(
        url=sample_url,
        provider="demo",
        duration_seconds=payload.duration_seconds,
        note="Demo response. Integrate with Replicate/Runway/Pika for real generation.",
    )


@app.post("/api/generate-image-video", response_model=GenerateResponse)
async def generate_image_video(
    image: UploadFile = File(...),
    duration_seconds: int = Form(30),
):
    # Simple file type validation
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload a valid image file")

    if duration_seconds > SAFE_MAX_SECONDS:
        raise HTTPException(status_code=400, detail="Demo limit: max 60 seconds")

    # Read at least once to ensure stream works (discard in demo)
    await image.read()

    # In real use, upload to storage and pass URL to the model; then return resulting video URL.
    sample_url = "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"

    return GenerateResponse(
        url=sample_url,
        provider="demo",
        duration_seconds=duration_seconds,
        note="Demo response. Integrate with Replicate/Runway/Pika for real generation.",
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
