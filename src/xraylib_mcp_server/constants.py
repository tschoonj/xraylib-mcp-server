"""String-to-integer constant resolution for xraylib macros.

xraylib uses integer constants for X-ray lines, shells, Auger transitions,
and Coster-Kronig transitions. This module provides functions to resolve
human-readable string names (e.g. "KL3_LINE", "K_SHELL") to their integer
values by introspecting the xraylib module at runtime.
"""

from __future__ import annotations

import xraylib

_LINE_CONSTANTS: dict[str, int] | None = None
_SHELL_CONSTANTS: dict[str, int] | None = None
_TRANS_CONSTANTS: dict[str, int] | None = None
_AUGER_CONSTANTS: dict[str, int] | None = None
_NIST_CONSTANTS: dict[str, int] | None = None


def _build_constants() -> None:
    """Build constant dictionaries by introspecting the xraylib module."""
    global _LINE_CONSTANTS, _SHELL_CONSTANTS, _TRANS_CONSTANTS
    global _AUGER_CONSTANTS, _NIST_CONSTANTS

    _LINE_CONSTANTS = {}
    _SHELL_CONSTANTS = {}
    _TRANS_CONSTANTS = {}
    _AUGER_CONSTANTS = {}
    _NIST_CONSTANTS = {}

    for name in dir(xraylib):
        val = getattr(xraylib, name)
        if not isinstance(val, int):
            continue
        if name.endswith("_LINE"):
            _LINE_CONSTANTS[name] = val
        elif name.endswith("_SHELL"):
            _SHELL_CONSTANTS[name] = val
        elif name.endswith("_TRANS"):
            _TRANS_CONSTANTS[name] = val
        elif name.endswith("_AUGER"):
            _AUGER_CONSTANTS[name] = val
        elif name.startswith("NIST_COMPOUND_"):
            _NIST_CONSTANTS[name] = val


def _ensure_built() -> None:
    """Ensure constant dictionaries are built."""
    if _LINE_CONSTANTS is None:
        _build_constants()


def _resolve(
    name: str,
    constants: dict[str, int],
    suffix: str,
    category: str,
) -> int:
    """Resolve a constant name to its integer value.

    Args:
        name: Constant name, optionally without suffix.
        constants: Dictionary of valid constants.
        suffix: Expected suffix (e.g. "_LINE").
        category: Human-readable category name for error messages.

    Returns:
        The integer value of the constant.

    Raises:
        ValueError: If the name is not a recognized constant.
    """
    normalized = name.strip().upper()
    if not normalized.endswith(suffix):
        normalized = normalized + suffix

    if normalized in constants:
        return constants[normalized]

    examples = sorted(constants.keys())[:20]
    more = len(constants) - len(examples)
    hint = ", ".join(examples)
    if more > 0:
        hint += f", ... and {more} more"
    raise ValueError(
        f"Unknown {category} constant: {name!r}. Valid names include: {hint}"
    )


def resolve_line(name: str) -> int:
    """Resolve a line constant name to its integer value.

    Args:
        name: Line constant name, e.g. "KL3_LINE", "KA_LINE", "LA1_LINE".
              The "_LINE" suffix is optional.

    Returns:
        The integer value of the line constant.

    Raises:
        ValueError: If the name is not a recognized line constant.
    """
    _ensure_built()
    assert _LINE_CONSTANTS is not None
    return _resolve(name, _LINE_CONSTANTS, "_LINE", "line")


def resolve_shell(name: str) -> int:
    """Resolve a shell constant name to its integer value.

    Args:
        name: Shell constant name, e.g. "K_SHELL", "L3_SHELL".
              The "_SHELL" suffix is optional.

    Returns:
        The integer value of the shell constant.

    Raises:
        ValueError: If the name is not a recognized shell constant.
    """
    _ensure_built()
    assert _SHELL_CONSTANTS is not None
    return _resolve(name, _SHELL_CONSTANTS, "_SHELL", "shell")


def resolve_transition(name: str) -> int:
    """Resolve a Coster-Kronig transition constant name to its integer value.

    Args:
        name: Transition constant name, e.g. "FL13_TRANS", "FM15_TRANS".
              The "_TRANS" suffix is optional.

    Returns:
        The integer value of the transition constant.

    Raises:
        ValueError: If the name is not a recognized transition constant.
    """
    _ensure_built()
    assert _TRANS_CONSTANTS is not None
    return _resolve(name, _TRANS_CONSTANTS, "_TRANS", "transition")


def resolve_auger(name: str) -> int:
    """Resolve an Auger transition constant name to its integer value.

    Args:
        name: Auger constant name, e.g. "K_L1L1_AUGER", "L2_M5M5_AUGER".
              The "_AUGER" suffix is optional.

    Returns:
        The integer value of the Auger constant.

    Raises:
        ValueError: If the name is not a recognized Auger constant.
    """
    _ensure_built()
    assert _AUGER_CONSTANTS is not None
    return _resolve(name, _AUGER_CONSTANTS, "_AUGER", "Auger")


def resolve_nist_compound(name: str) -> int:
    """Resolve a NIST compound constant name to its integer value.

    Args:
        name: NIST compound constant name, e.g. "NIST_COMPOUND_WATER_LIQUID"
              or just "WATER_LIQUID". The "NIST_COMPOUND_" prefix is optional.

    Returns:
        The integer value of the NIST compound constant.

    Raises:
        ValueError: If the name is not a recognized NIST compound constant.
    """
    _ensure_built()
    assert _NIST_CONSTANTS is not None
    normalized = name.strip().upper()
    if not normalized.startswith("NIST_COMPOUND_"):
        normalized = "NIST_COMPOUND_" + normalized
    if normalized in _NIST_CONSTANTS:
        return _NIST_CONSTANTS[normalized]

    examples = sorted(_NIST_CONSTANTS.keys())[:20]
    more = len(_NIST_CONSTANTS) - len(examples)
    hint = ", ".join(examples)
    if more > 0:
        hint += f", ... and {more} more"
    raise ValueError(
        f"Unknown NIST compound constant: {name!r}. Valid names include: {hint}"
    )


def list_lines() -> list[str]:
    """Return all valid line constant names."""
    _ensure_built()
    assert _LINE_CONSTANTS is not None
    return sorted(_LINE_CONSTANTS.keys())


def list_shells() -> list[str]:
    """Return all valid shell constant names."""
    _ensure_built()
    assert _SHELL_CONSTANTS is not None
    return sorted(_SHELL_CONSTANTS.keys())


def list_transitions() -> list[str]:
    """Return all valid Coster-Kronig transition constant names."""
    _ensure_built()
    assert _TRANS_CONSTANTS is not None
    return sorted(_TRANS_CONSTANTS.keys())


def list_auger_transitions() -> list[str]:
    """Return all valid Auger transition constant names."""
    _ensure_built()
    assert _AUGER_CONSTANTS is not None
    return sorted(_AUGER_CONSTANTS.keys())


def list_nist_compounds() -> list[str]:
    """Return all valid NIST compound constant names."""
    _ensure_built()
    assert _NIST_CONSTANTS is not None
    return sorted(_NIST_CONSTANTS.keys())
