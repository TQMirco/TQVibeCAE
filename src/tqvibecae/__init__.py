"""TQVibeCAE — CAD elettrico open source.

Package root. Runtime type checking attivo su tutto il package.
"""

from __future__ import annotations

from beartype.claw import beartype_this_package

beartype_this_package()

__version__ = "0.0.0"
