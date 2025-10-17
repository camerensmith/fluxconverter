from fastapi import FastAPI
from pydantic import BaseModel


class RunRequest(BaseModel):
    # Simple conversion job
    input_path: str
    output_dir: str
    output_format: str  # e.g. mp4, mp3, webp, wav
    # Optional preset/config future extension
    config_path: str | None = None
    preset_path: str | None = None


def create_app() -> FastAPI:
    app = FastAPI(title="FluxConvert API")

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.post("/run")
    async def run(req: RunRequest):
        # Stub hook where the orchestrator would schedule a job
        job = {
            "input": req.input_path,
            "output_dir": req.output_dir,
            "format": req.output_format,
        }
        return {"accepted": True, "job": job}

    return app

