"""Explicit configuration models and loader."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


DEFAULT_REPOSITORY_ROOT = Path("D:/ChantaResearchGroup")


@dataclass(slots=True)
class RepositoryConfig:
    root_path: Path = DEFAULT_REPOSITORY_ROOT
    inbox_folder: str = "00_Inbox"
    archive_folder: str = "99_Archive"

    @property
    def inbox_path(self) -> Path:
        return self.root_path / self.inbox_folder


@dataclass(slots=True)
class AppConfig:
    repository: RepositoryConfig
    dry_run_only: bool = True


def load_config(path: Path | None = None) -> AppConfig:
    """Load config from JSON file, otherwise return safe defaults.

    Config is explicit and minimal to keep behavior transparent.
    """

    if path is None:
        return AppConfig(repository=RepositoryConfig())

    data = json.loads(path.read_text(encoding="utf-8"))

    repository_data = data.get("repository", {})
    repository = RepositoryConfig(
        root_path=Path(repository_data.get("root_path", str(DEFAULT_REPOSITORY_ROOT))),
        inbox_folder=repository_data.get("inbox_folder", "00_Inbox"),
        archive_folder=repository_data.get("archive_folder", "99_Archive"),
    )

    return AppConfig(
        repository=repository,
        dry_run_only=bool(data.get("dry_run_only", True)),
    )
