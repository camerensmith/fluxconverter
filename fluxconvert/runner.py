from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import yaml

from .core.models import PipelineSpec


async def run_dry(config: Path, preset: Optional[Path] = None) -> None:
    config_text = Path(config).read_text()
    spec = PipelineSpec.model_validate_yaml(config_text)
    plan = {
        "steps": [
            {"name": s.name, "kind": s.kind, "params": s.params} for s in spec.steps
        ]
    }
    print(yaml.safe_dump(plan, sort_keys=False))

