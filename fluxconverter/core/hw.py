from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class HwCaps:
    has_nv: bool
    has_qsv: bool
    has_vtb: bool
    encoders: List[str]


def _get_ffmpeg_path() -> str:
    """Get FFmpeg path - bundled first, then system PATH."""
    import os
    from pathlib import Path
    
    # Try bundled FFmpeg first
    bundle_dir = Path(__file__).parent.parent / "bin"
    if os.name == 'nt':  # Windows
        bundled_ffmpeg = bundle_dir / "ffmpeg.exe"
    else:  # Linux/macOS
        bundled_ffmpeg = bundle_dir / "ffmpeg"
    
    if bundled_ffmpeg.exists():
        return str(bundled_ffmpeg)
    
    # Fallback to system PATH
    return "ffmpeg"

def _run_ffmpeg(args: list[str]) -> str:
    try:
        ffmpeg_path = _get_ffmpeg_path()
        out = subprocess.check_output([ffmpeg_path, *args], stderr=subprocess.STDOUT)
        return out.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def detect_hw_caps() -> HwCaps:
    hw_list = _run_ffmpeg(["-hide_banner", "-hwaccels"]).lower()
    encs = _run_ffmpeg(["-hide_banner", "-encoders"]).lower()
    return HwCaps(
        has_nv=("cuda" in hw_list or "nvdec" in hw_list),
        has_qsv=("qsv" in hw_list),
        has_vtb=("videotoolbox" in hw_list),
        encoders=[line.split()[1] for line in encs.splitlines() if line.strip().startswith("V.") and len(line.split()) > 1],
    )


def choose_encoder(hwc: HwCaps, prefer_hevc: bool = False) -> str:
    if prefer_hevc:
        if hwc.has_nv and "hevc_nvenc" in hwc.encoders:
            return "hevc_nvenc"
        if hwc.has_qsv and "hevc_qsv" in hwc.encoders:
            return "hevc_qsv"
        if hwc.has_vtb and "hevc_videotoolbox" in hwc.encoders:
            return "hevc_videotoolbox"
        return "libx265"
    # H.264
    if hwc.has_nv and "h264_nvenc" in hwc.encoders:
        return "h264_nvenc"
    if hwc.has_qsv and "h264_qsv" in hwc.encoders:
        return "h264_qsv"
    if hwc.has_vtb and "h264_videotoolbox" in hwc.encoders:
        return "h264_videotoolbox"
    return "libx264"

