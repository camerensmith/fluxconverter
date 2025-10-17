from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import yaml

from .core.models import PipelineSpec
from .core.ffmpeg import build_cpu_cmd, run_ffmpeg
from .core.hw import detect_hw_caps, choose_encoder


async def run_dry(config: Path, preset: Optional[Path] = None) -> None:
    config_text = Path(config).read_text()
    spec = PipelineSpec.model_validate_yaml(config_text)
    plan = {
        "steps": [
            {"name": s.name, "kind": s.kind, "params": s.params} for s in spec.steps
        ]
    }
    print(yaml.safe_dump(plan, sort_keys=False))


async def run_cpu_transcode(input_path: Path, output_path: Path, scale_filter: Optional[str] = None, prefer_hevc: bool = False) -> None:
    hwc = detect_hw_caps()
    vcodec = choose_encoder(hwc, prefer_hevc=prefer_hevc)
    # If selected encoder is hardware-specific, but we're forcing CPU path, map to libx264/265
    if vcodec.endswith("_nvenc") or vcodec.endswith("_qsv") or vcodec.endswith("_videotoolbox"):
        vcodec = "libx265" if prefer_hevc else "libx264"
    cmd = build_cpu_cmd(str(input_path), str(output_path), vfilter=scale_filter, vcodec=vcodec)
    async for prog in run_ffmpeg(cmd):
        # Minimal progress print; integrate with API/GUI later
        if prog.frame is not None or prog.fps is not None or prog.speed is not None:
            print(f"frame={prog.frame} fps={prog.fps} speed={prog.speed}")

