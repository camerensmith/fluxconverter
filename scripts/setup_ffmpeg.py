#!/usr/bin/env python3
"""
Setup script to download FFmpeg for FluxConverter.
Run this after installing the package to get FFmpeg.
"""
import os
import sys
import zipfile
import urllib.request
from pathlib import Path

def download_ffmpeg():
    """Download FFmpeg static build for the current platform."""
    if os.name != 'nt':
        print("This script currently only supports Windows. Please install FFmpeg manually.")
        return False
    
    # BtbN's FFmpeg builds (Windows x64)
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    # Create bin directory
    bin_dir = Path(__file__).parent.parent / "fluxconverter" / "bin"
    bin_dir.mkdir(exist_ok=True)
    
    if (bin_dir / "ffmpeg.exe").exists():
        print("FFmpeg already exists. Skipping download.")
        return True
    
    zip_path = bin_dir / "ffmpeg.zip"
    
    print("Downloading FFmpeg (167MB)...")
    try:
        urllib.request.urlretrieve(url, zip_path)
        print("Extracting FFmpeg...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract ffmpeg.exe from the nested directory
            for member in zip_ref.namelist():
                if member.endswith('ffmpeg.exe'):
                    # Extract to bin directory
                    zip_ref.extract(member, bin_dir)
                    # Move from nested directory to bin root
                    extracted_path = bin_dir / member
                    final_path = bin_dir / "ffmpeg.exe"
                    if extracted_path.exists():
                        extracted_path.rename(final_path)
                        print(f"FFmpeg installed to: {final_path}")
                        break
        
        # Clean up
        zip_path.unlink()
        
        # Remove empty nested directories
        for item in bin_dir.iterdir():
            if item.is_dir():
                try:
                    item.rmdir()
                except OSError:
                    pass  # Directory not empty, skip
        
        print("FFmpeg setup complete!")
        return True
        
    except Exception as e:
        print(f"Error downloading FFmpeg: {e}")
        return False

if __name__ == "__main__":
    success = download_ffmpeg()
    sys.exit(0 if success else 1)
