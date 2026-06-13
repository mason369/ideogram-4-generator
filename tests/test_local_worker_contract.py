from __future__ import annotations

import pytest

from ideogram_tool import local_worker


def test_local_worker_rejects_low_system_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IDEOGRAM_MIN_SYSTEM_MEMORY_GB", "24")
    monkeypatch.setattr(local_worker, "_system_memory_gib", lambda: 15.5)

    with pytest.raises(RuntimeError, match="Increase WSL memory"):
        local_worker._assert_minimum_system_memory()


def test_local_worker_allows_enough_system_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IDEOGRAM_MIN_SYSTEM_MEMORY_GB", "24")
    monkeypatch.setattr(local_worker, "_system_memory_gib", lambda: 32.0)

    local_worker._assert_minimum_system_memory()
