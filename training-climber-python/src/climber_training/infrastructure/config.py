from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_data_path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    database_url: str

    @classmethod
    def load(cls) -> "Settings":
        data_dir = Path(os.environ.get("CLIMBER_TRAINING_DATA_DIR") or user_data_path("ClimberTraining", "ClimberTraining"))
        data_dir.mkdir(parents=True, exist_ok=True)
        return cls(data_dir=data_dir, database_url=f"sqlite:///{(data_dir / 'climber_training.db').as_posix()}")
