from __future__ import annotations
import pathlib
import typer
from rich.console import Console
from typing import Optional, List
from .core.schema import PipelineSpec
from .core.runner import Runner
from .presets import load_preset_path
from .api import run_api

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()

@app.command(help="Run the local REST API (for GUI/remote control).")
def api(port: int = typer.Option(7845, help="Port for the API")):
    run_api(port)

@app.callback(invoke_without_command=True)
def main(
    input_paths: List[str] = typer.Argument(None),
    config: Optional[pathlib.Path] = typer.Option(None, "--config", "-c", help="YAML file"),
    preset: Optional[str] = typer.Option(None, "--preset", help="Preset name (presets/<name>.yaml)"),
    out: Optional[pathlib.Path] = typer.Option(None, "--out", help="Override output path"),
    dump_config: bool = typer.Option(False, "--dump-config", help="Print the effective YAML/JSON"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Plan without executing"),
    watch: bool = typer.Option(False, "--watch", help="Enable watch mode if supported by spec"),
):
    if config:
        spec = PipelineSpec.from_yaml(config.read_text())
    else:
        name = preset or "web-1080p"
        cfg_path = load_preset_path(name)
        spec = PipelineSpec.from_yaml(cfg_path.read_text())
        if input_paths:
            spec.inputs[0].path = str(pathlib.Path(input_paths[0]).resolve())
        if out:
            for o in spec.outputs:
                o.path = str(out.resolve())

    if dump_config:
        console.print(spec.model_dump())
        raise typer.Exit(0)

    if dry_run:
        Runner.dry_run(spec)
        raise typer.Exit(0)

    Runner.run(spec, watch=watch)

if __name__ == "__main__":
    app()
