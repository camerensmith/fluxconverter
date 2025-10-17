import asyncio
from pathlib import Path
from typing import Optional

import typer
import uvicorn
import yaml

from .core.models import PipelineSpec
from .runner import run_dry
from .api import create_app
from .gui.main import main as gui_main


app = typer.Typer(help="FluxConvert CLI")


@app.command()
def dump_config(config: Path):
    """Print the resolved configuration (YAML)."""
    spec = PipelineSpec.model_validate_yaml(config.read_text())
    typer.echo(yaml.safe_dump(spec.model_dump(), sort_keys=False))


@app.command()
def dry_run(config: Path, preset: Optional[Path] = None):
    """Validate and print execution plan without running."""
    asyncio.run(run_dry(config, preset))


@app.command("api")
def run_api(port: int = 7845, host: str = "127.0.0.1"):
    """Start local API server."""
    uvicorn.run(create_app(), host=host, port=port)


@app.command("gui")
def run_gui():
    """Start the GUI application."""
    gui_main()


def main():  # for python -m fluxconvert
    app()


if __name__ == "__main__":
    main()

