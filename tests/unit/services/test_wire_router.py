"""Test wire router ortogonale."""

from __future__ import annotations

from tqvibecae.services.rendering.wire_router import route_orthogonal


def test_aligned_pins_single_segment() -> None:
    segments = route_orthogonal((0.0, 0.0), (10.0, 0.0))
    assert len(segments) == 1


def test_diagonal_pins_two_orthogonal_segments() -> None:
    segments = route_orthogonal((0.0, 0.0), (10.0, 20.0))
    assert len(segments) == 2
    for seg in segments:
        horizontal = abs(seg.y1_mm - seg.y2_mm) < 1e-9
        vertical = abs(seg.x1_mm - seg.x2_mm) < 1e-9
        assert horizontal or vertical


def test_snap_quantizes_bend_point() -> None:
    segments = route_orthogonal((0.0, 0.0), (13.0, 17.0), snap_mm=5.0)
    assert len(segments) == 2
    assert segments[-1].x2_mm == 15.0
    assert segments[-1].y2_mm == 15.0
