#!/usr/bin/env python3
"""
Download AI upscaling tools for FluxConverter.
Downloads Real-ESRGAN and other AI tools as binaries.
"""
import os
import sys
import zipfile
import urllib.request
from pathlib import Path

def download_real_esrgan():
    """Download Real-ESRGAN executable."""
    if os.name != 'nt':
        print("This script currently only supports Windows. Please install Real-ESRGAN manually.")
        return False
    
    # Real-ESRGAN releases
    url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.4/realesrgan-ncnn-vulkan-20220424-windows.zip"
    
    # Create bin directory
    bin_dir = Path(__file__).parent.parent / "fluxconverter" / "bin"
    bin_dir.mkdir(exist_ok=True)
    
    if (bin_dir / "realesrgan-ncnn-vulkan.exe").exists():
        print("Real-ESRGAN already exists. Skipping download.")
        return True
    
    zip_path = bin_dir / "realesrgan.zip"
    
    print("Downloading Real-ESRGAN...")
    try:
        urllib.request.urlretrieve(url, zip_path)
        print("Extracting Real-ESRGAN...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract all files
            zip_ref.extractall(bin_dir)
            print(f"Real-ESRGAN installed to: {bin_dir}")
        
        # Clean up
        zip_path.unlink()
        
        print("Real-ESRGAN setup complete!")
        return True
        
    except Exception as e:
        print(f"Error downloading Real-ESRGAN: {e}")
        return False

def download_models():
    """Download AI models."""
    bin_dir = Path(__file__).parent.parent / "fluxconverter" / "bin"
    models_dir = bin_dir / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Real-ESRGAN models
    models = {
        "RealESRGAN_x4plus.bin": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.bin",
        "RealESRGAN_x4plus.param": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.param",
        "RealESRGAN_x4plus_anime_6B.bin": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.bin",
        "RealESRGAN_x4plus_anime_6B.param": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.param"
    }
    
    print("Downloading AI models...")
    for model_name, model_url in models.items():
        model_path = models_dir / model_name
        if model_path.exists():
            print(f"Model {model_name} already exists. Skipping.")
            continue
            
        try:
            print(f"Downloading {model_name}...")
            urllib.request.urlretrieve(model_url, model_path)
            print(f"Downloaded {model_name}")
        except Exception as e:
            print(f"Error downloading {model_name}: {e}")
    
    print("Model download complete!")

if __name__ == "__main__":
    print("Setting up AI upscaling tools for FluxConverter...")
    
    success = download_real_esrgan()
    if success:
        download_models()
    
    sys.exit(0 if success else 1)
