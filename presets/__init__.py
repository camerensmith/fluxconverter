from importlib.resources import files

def load_preset_path(name: str):
    pkg_files = files(__package__)
    p = pkg_files / f"{name}.yaml"
    if not p.is_file():
        raise FileNotFoundError(f"Preset not found: {name}")
    return p
