from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field
import yaml


class Step(BaseModel):
    name: str
    kind: Literal["decode", "filter", "encode"]
    params: dict = Field(default_factory=dict)


class PipelineSpec(BaseModel):
    steps: list[Step]

    @classmethod
    def model_validate_yaml(cls, yaml_text: str) -> "PipelineSpec":
        data = yaml.safe_load(yaml_text)
        return cls.model_validate(data)

