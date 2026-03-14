from pathlib import Path

from chanta_perma_memory.config.settings import load_config


def test_load_config_defaults_to_dry_run_and_expected_paths() -> None:
    config = load_config()

    assert config.dry_run_only is True
    assert config.repository.root_path == Path("D:/ChantaResearchGroup")
    assert config.repository.inbox_path == Path("D:/ChantaResearchGroup/00_Inbox")
