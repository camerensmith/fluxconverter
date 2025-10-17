from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from .core.schema import PipelineSpec
from .core.runner import Runner

class RunRequest(BaseModel):
    spec: PipelineSpec
    dry_run: bool = False

def make_app():
    app = FastAPI(title="FluxConvert API")

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.post("/run")
    def run(req: RunRequest):
        if req.dry_run:
            Runner.dry_run(req.spec)
            return {"status": "dry-run"}
        Runner.run(req.spec, watch=False)
        return {"status": "started"}

    return app

def run_api(port: int = 7845):
    app = make_app()
    uvicorn.run(app, host="127.0.0.1", port=port)
