from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Iterable, Literal, Any
from importlib.metadata import entry_points

MediaKind = Literal["audio", "video", "image"]

@dataclass
class Caps:
    kinds: list[MediaKind]
    formats: list[str]

class NodePlugin(Protocol):
    def name(self) -> str: ...
    def capabilities(self) -> Caps: ...
    def configure(self, params: dict[str, Any]) -> None: ...
    def process(self, buffer: bytes) -> bytes: ...  # placeholder

def discover_plugins(group: str = "fluxconvert.plugins") -> Iterable[Any]:
    eps = entry_points().get(group, [])
    for ep in eps:
        yield ep.load()
