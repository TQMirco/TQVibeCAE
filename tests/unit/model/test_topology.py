"""Test topologia elettrica."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from tqvibecae.model.entity_types import CORE, NET
from tqvibecae.model.topology import Core, LengthSpecification, Net


def test_core_rejects_zero_cross_section() -> None:
    with pytest.raises(ValidationError):
        Core(
            id=uuid4(),
            entity_type=CORE,
            color_code="BK",
            cross_section_mm2=0.0,
        )


def test_net_requires_two_points_when_non_empty() -> None:
    with pytest.raises(ValidationError):
        Net(
            id=uuid4(),
            entity_type=NET,
            connection_point_ids=(uuid4(),),
        )


def test_length_spec_roundtrip() -> None:
    spec = LengthSpecification(value_mm=1000.0, source="estimated")
    restored = LengthSpecification.model_validate(spec.model_dump(mode="json"))
    assert restored == spec
