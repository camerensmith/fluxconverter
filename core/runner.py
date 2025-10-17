from __future__ import annotations
import time
from dataclasses import dataclass
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from .schema import PipelineSpec

console = Console()

@dataclass
class Job:
    input_path: str
    output_path: str
    spec: PipelineSpec

class Runner:
    @staticmethod
    def dry_run(spec: PipelineSpec):
        console.rule("[bold]DRY RUN[/]")
        for i, inp in enumerate(spec.inputs, 1):
            console.print(f"[cyan]Input {i}[/]: path={inp.path} include={inp.include} watch={inp.watch}")
        for idx, node in enumerate(spec.pipeline, 1):
            console.print(f"[magenta]Step {idx}[/]: {node.node} when={node.when} params={node.params}")
        for o in spec.outputs:
            console.print(f"[green]Output[/]: path={o.path} container={o.container} pattern={o.pattern}")
        console.print(f"[yellow]OnError[/]: {spec.on_error.strategy} -> {spec.on_error.move_to}")

    @staticmethod
    def run(spec: PipelineSpec, watch: bool = False):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            transient=False,
        ) as progress:
            task = progress.add_task("Processing (simulated)", total=100)
            for _ in range(5):
                time.sleep(0.25)
                progress.advance(task, 20)
        console.print("[bold green]Completed (simulated).[/]")
