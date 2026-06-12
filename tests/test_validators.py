from __future__ import annotations

import pytest

from ideogram_tool.schemas import IdeogramRequest
from ideogram_tool.validators import (
    aspect_ratio_for_size,
    normalize_seed,
    require_official_resolution,
    validate_dimensions,
)


def test_dimensions_follow_telknet_rules() -> None:
    validate_dimensions(2048, 512)
    with pytest.raises(ValueError, match="multiple of 16"):
        validate_dimensions(1025, 1024)
    with pytest.raises(ValueError, match="between 1:6"):
        validate_dimensions(2048, 256)


def test_zero_seed_is_randomized_and_candidate_range_is_checked(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []
    monkeypatch.setattr("ideogram_tool.validators.secrets.randbelow", lambda upper: calls.append(upper) or 41)
    assert normalize_seed(0, 4) == 42
    assert calls == [2147483644]
    with pytest.raises(ValueError, match="seed range exceeds"):
        normalize_seed(2147483647, 2)


def test_official_resolution_is_strict() -> None:
    assert require_official_resolution(IdeogramRequest(prompt="x", width=2048, height=2048)) == "2048x2048"
    with pytest.raises(ValueError, match="fixed resolution list"):
        require_official_resolution(IdeogramRequest(prompt="x", width=1152, height=2048))


def test_magic_aspect_bucket_is_strict() -> None:
    assert aspect_ratio_for_size(2048, 2048) == "1x1"
    assert aspect_ratio_for_size(1440, 2560) == "9x16"
    with pytest.raises(ValueError, match="supported aspect ratio"):
        aspect_ratio_for_size(1360, 2048)
