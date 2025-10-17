from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Any
import yaml

class InputSpec(BaseModel):
    path: str
    include: List[str] = Field(default_factory=list)
    watch: bool = False

class NodeSpec(BaseModel):
    node: str
    when: Optional[str] = None
    params: dict[str, Any] = Field(default_factory=dict)

class OutputSpec(BaseModel):
    path: str
    container: str
    pattern: str

class OnError(BaseModel):
    strategy: str = "continue"
    move_to: Optional[str] = None

class PipelineSpec(BaseModel):
    inputs: List[InputSpec]
    pipeline: List[NodeSpec]
    outputs: List[OutputSpec]
    on_error: OnError = Field(default_factory=OnError)

    @classmethod
    def from_yaml(cls, s: str) -> "PipelineSpec":
        data = yaml.safe_load(s)
        return cls.model_validate(data)
