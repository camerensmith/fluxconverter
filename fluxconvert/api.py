from fastapi import FastAPI
from pydantic import BaseModel


class RunRequest(BaseModel):
    config_path: str
    preset_path: str | None = None


def create_app() -> FastAPI:
    app = FastAPI(title="FluxConvert API")

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.post("/run")
    async def run(req: RunRequest):
        # Stub hook where the orchestrator would schedule a job
        return {"accepted": True, "config": req.config_path, "preset": req.preset_path}

    return app

