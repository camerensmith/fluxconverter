from __future__ import annotations

import asyncio
import shlex
from dataclasses import dataclass
from typing import AsyncIterator, List, Optional


@dataclass
class FfmpegProgress:
    frame: Optional[int] = None
    fps: Optional[float] = None
    bitrate: Optional[str] = None
    speed: Optional[str] = None
    out_time_ms: Optional[int] = None


def build_cpu_cmd(input_path: str, output_path: str, vfilter: Optional[str] = None, vcodec: str = "libx264", acodec: str = "aac", extra: Optional[List[str]] = None) -> List[str]:
    from .hw import _get_ffmpeg_path
    ffmpeg_path = _get_ffmpeg_path()
    cmd = [
        ffmpeg_path, "-y",
        "-hide_banner", "-nostdin",
        "-progress", "pipe:2",
        "-i", input_path,
    ]
    if vfilter:
        cmd += ["-vf", vfilter]
    cmd += ["-c:v", vcodec, "-c:a", acodec]
    if extra:
        cmd += list(extra)
    cmd += [output_path]
    return cmd


async def run_ffmpeg(cmd: List[str]) -> AsyncIterator[FfmpegProgress]:
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    assert process.stderr is not None
    async for raw in process.stderr:
        line = raw.decode("utf-8", errors="ignore").strip()
        if not line or "=" not in line:
            continue
        key, val = line.split("=", 1)
        prog = FfmpegProgress()
        if key == "frame":
            try:
                prog.frame = int(val)
            except ValueError:
                pass
        elif key == "fps":
            try:
                prog.fps = float(val)
            except ValueError:
                pass
        elif key == "bitrate":
            prog.bitrate = val
        elif key == "speed":
            prog.speed = val
        elif key == "out_time_ms":
            try:
                prog.out_time_ms = int(val)
            except ValueError:
                pass
        yield prog
    await process.wait()
    if process.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {process.returncode}")

