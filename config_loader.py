import yaml
from pathlib import Path
from typing import Dict, List, Literal
from pydantic import BaseModel, field_validator

# -- Define your models (same as before) --

class TimeFrameConfig(BaseModel):
    from_time: str
    to_time: str
    resolution: str

class ServiceMetricConfig(BaseModel):
    name: str
    id: str
    threshold_ms: int
    metrics: Dict[str, str]

class DatabaseMetricConfig(BaseModel):
    name: str
    id: str
    metrics: Dict[str, str]

class FullConfig(BaseModel):
    debug: bool = True
    timeframes: Dict[Literal["services", "databases"], TimeFrameConfig]
    services: List[ServiceMetricConfig]
    databases: List[DatabaseMetricConfig]


# -- Load config once and expose it here --
def _load_config() -> FullConfig:
    with open("config.yaml", "r") as f:
        data = yaml.safe_load(f)
    return FullConfig(**data)

# Singleton-like: only load once, then reuse
_config: FullConfig | None = None

# Using a lazy loading approach
def get_config() -> FullConfig:
    global _config
    if _config is None:
        _config = _load_config()
    return _config


