"""
Loads YAML-based agent and task configurations so crew.py can access them as
Python dictionaries:

    from .config import agents_config, tasks_config
"""

from pathlib import Path
import yaml

# Folder that contains this file:
_BASE = Path(__file__).parent

def _load_yaml(rel_path: str) -> dict:
    yaml_path = _BASE / "config" / rel_path
    with yaml_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

agents_config = _load_yaml("agents.yaml")
tasks_config  = _load_yaml("tasks.yaml")