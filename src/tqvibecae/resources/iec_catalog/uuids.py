"""UUID deterministici catalogo IEC."""

from __future__ import annotations

from uuid import UUID, uuid5

IEC_NAMESPACE = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


def iec_uuid(kind: str, name: str) -> UUID:
    """Genera UUID5 stabile per celle e composizioni."""
    return uuid5(IEC_NAMESPACE, f"{kind}:{name}")
