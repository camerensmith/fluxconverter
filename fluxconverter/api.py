import asyncio
import uuid
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .core.ffmpeg import build_cpu_cmd, run_ffmpeg
from .core.hw import detect_hw_caps, choose_encoder


class RunRequest(BaseModel):
    # Simple conversion job
    input_path: str
    output_dir: str
    output_format: str  # e.g. mp4, mp3, webp, wav
    options: dict = {}  # Additional options (AI upscaling, quality, etc.)
    # Optional preset/config future extension
    config_path: str | None = None
    preset_path: str | None = None


# In-memory job storage (replace with database in production)
jobs: Dict[str, Dict[str, Any]] = {}


def create_app() -> FastAPI:
    app = FastAPI(title="FluxConverter API")

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.post("/run")
    async def run(req: RunRequest):
        # Validate input file exists
        input_path = Path(req.input_path)
        if not input_path.exists():
            raise HTTPException(status_code=400, detail=f"Input file not found: {req.input_path}")
        
        # Create output directory if needed
        output_dir = Path(req.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename
        output_name = input_path.stem + f".{req.output_format}"
        output_path = output_dir / output_name
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Store job info
        jobs[job_id] = {
            "id": job_id,
            "input_path": str(input_path),
            "output_path": str(output_path),
            "format": req.output_format,
            "status": "queued",
            "progress": 0,
            "error": None
        }
        
        # Start conversion in background
        asyncio.create_task(process_conversion(job_id, input_path, output_path, req.output_format, req.options))
        
        return {"accepted": True, "job_id": job_id, "output_path": str(output_path)}

    @app.get("/status/{job_id}")
    async def get_status(job_id: str):
        if job_id not in jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        return jobs[job_id]

    return app


async def process_conversion(job_id: str, input_path: Path, output_path: Path, output_format: str, options: dict = None):
    """Process a conversion job in the background."""
    if options is None:
        options = {}
        
    try:
        jobs[job_id]["status"] = "processing"
        
        # Check if this is an image with AI upscaling
        if output_format in ["png", "jpg", "jpeg", "webp", "bmp", "tiff"] and options.get("ai_upscaling"):
            await process_ai_upscaling(job_id, input_path, output_path, options)
        else:
            # Regular FFmpeg conversion
            await process_ffmpeg_conversion(job_id, input_path, output_path, output_format, options)
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


async def process_ai_upscaling(job_id: str, input_path: Path, output_path: Path, options: dict):
    """Process AI upscaling for images."""
    try:
        jobs[job_id]["progress"] = 10
        
        # For now, simulate AI processing (will implement Real-ESRGAN later)
        ai_model = options.get("ai_model", "Real-ESRGAN")
        ai_scale = options.get("ai_scale", "2x")
        
        # Simulate AI processing time
        for i in range(10, 90, 10):
            jobs[job_id]["progress"] = i
            await asyncio.sleep(0.5)  # Simulate processing time
        
        # For now, just copy the file (placeholder for Real-ESRGAN)
        import shutil
        shutil.copy2(input_path, output_path)
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = f"AI upscaling failed: {str(e)}"


async def process_ffmpeg_conversion(job_id: str, input_path: Path, output_path: Path, output_format: str, options: dict):
    """Process regular FFmpeg conversion."""
    # Detect hardware capabilities
    hw_caps = detect_hw_caps()
    
    # Choose appropriate codec based on format
    if output_format in ["mp4", "webm"]:
        vcodec = choose_encoder(hw_caps, prefer_hevc=(output_format == "mp4"))
        acodec = "aac"
        cmd = build_cpu_cmd(str(input_path), str(output_path), vcodec=vcodec, acodec=acodec)
    elif output_format in ["mp3", "wav", "flac", "m4a"]:
        # Audio-only conversion
        acodec_map = {
            "mp3": "libmp3lame",
            "wav": "pcm_s16le", 
            "flac": "flac",
            "m4a": "aac"
        }
        acodec = acodec_map.get(output_format, "aac")
        cmd = build_cpu_cmd(str(input_path), str(output_path), vcodec="copy", acodec=acodec)
    else:
        # Image or other formats - use copy for now
        cmd = build_cpu_cmd(str(input_path), str(output_path), vcodec="copy", acodec="copy")
    
    # Run conversion with progress tracking
    frame_count = 0
    async for progress in run_ffmpeg(cmd):
        if progress.frame is not None:
            frame_count = progress.frame
            # Simple progress calculation (could be more sophisticated)
            jobs[job_id]["progress"] = min(90, frame_count)  # Cap at 90% until complete
    
    jobs[job_id]["status"] = "completed"
    jobs[job_id]["progress"] = 100

