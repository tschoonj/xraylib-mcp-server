"""xraylib MCP Server - X-ray interaction data via Model Context Protocol."""

from __future__ import annotations

import argparse
import json
from typing import Any

import xraylib
from mcp.server.fastmcp import FastMCP

from xraylib_mcp_server.constants import (
    list_auger_transitions,
    list_lines,
    list_nist_compounds,
    list_shells,
    list_transitions,
    resolve_auger,
    resolve_line,
    resolve_shell,
    resolve_transition,
)

# Cache static lists at module load time
_NIST_COMPOUNDS: list[str] = list(xraylib.GetCompoundDataNISTList())
_RADIONUCLIDES: list[str] = list(xraylib.GetRadioNuclideDataList())

mcp = FastMCP(
    "xraylib X-ray Interaction Data Server",
    instructions=(
        "When querying compound/material data, match the user's query against "
        "the NIST compound list below and use GetCompoundDataNISTByName with the "
        "exact name before falling back to CompoundParser. The NIST database "
        "provides vetted compositions and densities for common materials.\n"
        "Available NIST compounds: " + ", ".join(_NIST_COMPOUNDS) + "\n\n"
        "When the user asks about something that looks like a radionuclide "
        "(e.g. 55Fe, 241Am, 109Cd), match it against the radionuclide list "
        "below and use GetRadioNuclideDataByName to retrieve its X-ray lines, "
        "intensities, and gamma data.\n"
        "Available radionuclides: " + ", ".join(_RADIONUCLIDES)
    ),
)


def _result_json(
    func_name: str,
    result: Any,
    units: str,
    inputs: dict[str, Any],
) -> str:
    """Format a successful result as JSON."""
    return json.dumps(
        {
            "function": func_name,
            "result": result,
            "units": units,
            "inputs": inputs,
        }
    )


def _error_json(func_name: str, error: Exception) -> str:
    """Format an error as JSON."""
    return json.dumps({"function": func_name, "error": str(error)})


# ---------------------------------------------------------------------------
# Utility tools
# ---------------------------------------------------------------------------


@mcp.tool()
def AtomicNumberToSymbol(Z: int) -> str:
    """Convert an atomic number to its element symbol.

    Args:
        Z: Atomic number (1-120)
    """
    try:
        result = xraylib.AtomicNumberToSymbol(Z)
        return _result_json("AtomicNumberToSymbol", result, "", {"Z": Z})
    except Exception as e:
        return _error_json("AtomicNumberToSymbol", e)


@mcp.tool()
def SymbolToAtomicNumber(symbol: str) -> str:
    """Convert an element symbol to its atomic number.

    Args:
        symbol: Element symbol, e.g. "Fe", "Cu", "Au"
    """
    try:
        result = xraylib.SymbolToAtomicNumber(symbol)
        return _result_json("SymbolToAtomicNumber", result, "", {"symbol": symbol})
    except Exception as e:
        return _error_json("SymbolToAtomicNumber", e)


@mcp.tool()
def AtomicWeight(Z: int) -> str:
    """Get the atomic weight of an element.

    Args:
        Z: Atomic number (1-120)
    """
    try:
        result = xraylib.AtomicWeight(Z)
        return _result_json("AtomicWeight", result, "g/mol", {"Z": Z})
    except Exception as e:
        return _error_json("AtomicWeight", e)


@mcp.tool()
def ElementDensity(Z: int) -> str:
    """Get the density of a pure element.

    Args:
        Z: Atomic number (1-120)
    """
    try:
        result = xraylib.ElementDensity(Z)
        return _result_json("ElementDensity", result, "g/cm3", {"Z": Z})
    except Exception as e:
        return _error_json("ElementDensity", e)


@mcp.tool()
def ElectronConfig(Z: int, shell: str) -> str:
    """Get the electron configuration for a given shell of an element.

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL", "M5_SHELL"
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.ElectronConfig(Z, shell_int)
        return _result_json(
            "ElectronConfig", result, "electrons", {"Z": Z, "shell": shell}
        )
    except Exception as e:
        return _error_json("ElectronConfig", e)


@mcp.tool()
def CompoundParser(compound: str) -> str:
    """Parse a chemical compound formula and return its composition.

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O", "Ca5(PO4)3F"
    """
    try:
        result = xraylib.CompoundParser(compound)
        return _result_json("CompoundParser", result, "", {"compound": compound})
    except Exception as e:
        return _error_json("CompoundParser", e)


@mcp.tool()
def Atomic_Factors(Z: int, E: float, q: float, debye_factor: float) -> str:
    """Calculate atomic factors f0, f', and f'' for an element.

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
        q: Momentum transfer in 1/Angstrom
        debye_factor: Debye temperature factor
    """
    try:
        f0, fp, fpp = xraylib.Atomic_Factors(Z, E, q, debye_factor)
        return _result_json(
            "Atomic_Factors",
            {"f0": f0, "f_prime": fp, "f_prime2": fpp},
            "",
            {"Z": Z, "E_keV": E, "q": q, "debye_factor": debye_factor},
        )
    except Exception as e:
        return _error_json("Atomic_Factors", e)


# ---------------------------------------------------------------------------
# Line/edge/shell properties
# ---------------------------------------------------------------------------


@mcp.tool()
def LineEnergy(Z: int, line: str) -> str:
    """Get the energy of an X-ray fluorescence line.

    Args:
        Z: Atomic number (1-120)
        line: Line name, e.g. "KL3_LINE", "KA_LINE", "LA1_LINE"
    """
    try:
        line_int = resolve_line(line)
        result = xraylib.LineEnergy(Z, line_int)
        return _result_json("LineEnergy", result, "keV", {"Z": Z, "line": line})
    except Exception as e:
        return _error_json("LineEnergy", e)


@mcp.tool()
def EdgeEnergy(Z: int, shell: str) -> str:
    """Get the absorption edge energy for a given shell.

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL", "M5_SHELL"
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.EdgeEnergy(Z, shell_int)
        return _result_json("EdgeEnergy", result, "keV", {"Z": Z, "shell": shell})
    except Exception as e:
        return _error_json("EdgeEnergy", e)


@mcp.tool()
def FluorYield(Z: int, shell: str) -> str:
    """Get the fluorescence yield for a given shell.

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.FluorYield(Z, shell_int)
        return _result_json("FluorYield", result, "", {"Z": Z, "shell": shell})
    except Exception as e:
        return _error_json("FluorYield", e)


@mcp.tool()
def JumpFactor(Z: int, shell: str) -> str:
    """Get the jump factor for a given absorption edge.

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.JumpFactor(Z, shell_int)
        return _result_json("JumpFactor", result, "", {"Z": Z, "shell": shell})
    except Exception as e:
        return _error_json("JumpFactor", e)


@mcp.tool()
def RadRate(Z: int, line: str) -> str:
    """Get the radiative rate for a given fluorescence line.

    Args:
        Z: Atomic number (1-120)
        line: Line name, e.g. "KL3_LINE", "KA_LINE"
    """
    try:
        line_int = resolve_line(line)
        result = xraylib.RadRate(Z, line_int)
        return _result_json("RadRate", result, "", {"Z": Z, "line": line})
    except Exception as e:
        return _error_json("RadRate", e)


@mcp.tool()
def AtomicLevelWidth(Z: int, shell: str) -> str:
    """Get the natural width of an atomic level.

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.AtomicLevelWidth(Z, shell_int)
        return _result_json("AtomicLevelWidth", result, "keV", {"Z": Z, "shell": shell})
    except Exception as e:
        return _error_json("AtomicLevelWidth", e)


# ---------------------------------------------------------------------------
# Element cross-sections (cm2/g)
# ---------------------------------------------------------------------------


@mcp.tool()
def CS_Total(Z: int, E: float) -> str:
    """Calculate the total cross section of an element (cm2/g).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
    """
    try:
        result = xraylib.CS_Total(Z, E)
        return _result_json("CS_Total", result, "cm2/g", {"Z": Z, "E_keV": E})
    except Exception as e:
        return _error_json("CS_Total", e)


@mcp.tool()
def CS_Photo(Z: int, E: float) -> str:
    """Calculate the photoionization cross section of an element (cm2/g).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
    """
    try:
        result = xraylib.CS_Photo(Z, E)
        return _result_json("CS_Photo", result, "cm2/g", {"Z": Z, "E_keV": E})
    except Exception as e:
        return _error_json("CS_Photo", e)


@mcp.tool()
def CS_Rayl(Z: int, E: float) -> str:
    """Calculate the Rayleigh scattering cross section of an element (cm2/g).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
    """
    try:
        result = xraylib.CS_Rayl(Z, E)
        return _result_json("CS_Rayl", result, "cm2/g", {"Z": Z, "E_keV": E})
    except Exception as e:
        return _error_json("CS_Rayl", e)


@mcp.tool()
def CS_Compt(Z: int, E: float) -> str:
    """Calculate the Compton scattering cross section of an element (cm2/g).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
    """
    try:
        result = xraylib.CS_Compt(Z, E)
        return _result_json("CS_Compt", result, "cm2/g", {"Z": Z, "E_keV": E})
    except Exception as e:
        return _error_json("CS_Compt", e)


@mcp.tool()
def CS_KN(E: float) -> str:
    """Calculate the Klein-Nishina cross section (barn/electron).

    Args:
        E: Photon energy in keV
    """
    try:
        result = xraylib.CS_KN(E)
        return _result_json("CS_KN", result, "barn/electron", {"E_keV": E})
    except Exception as e:
        return _error_json("CS_KN", e)


@mcp.tool()
def CS_Energy(Z: int, E: float) -> str:
    """Calculate the mass energy-absorption cross section of an element (cm2/g).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
    """
    try:
        result = xraylib.CS_Energy(Z, E)
        return _result_json("CS_Energy", result, "cm2/g", {"Z": Z, "E_keV": E})
    except Exception as e:
        return _error_json("CS_Energy", e)


# ---------------------------------------------------------------------------
# Element cross-sections (barn/atom)
# ---------------------------------------------------------------------------


@mcp.tool()
def CSb_Total(Z: int, E: float) -> str:
    """Calculate the total cross section of an element (barn/atom).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
    """
    try:
        result = xraylib.CSb_Total(Z, E)
        return _result_json("CSb_Total", result, "barn/atom", {"Z": Z, "E_keV": E})
    except Exception as e:
        return _error_json("CSb_Total", e)


@mcp.tool()
def CSb_Photo(Z: int, E: float) -> str:
    """Calculate the photoionization cross section of an element (barn/atom).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
    """
    try:
        result = xraylib.CSb_Photo(Z, E)
        return _result_json("CSb_Photo", result, "barn/atom", {"Z": Z, "E_keV": E})
    except Exception as e:
        return _error_json("CSb_Photo", e)


@mcp.tool()
def CSb_Rayl(Z: int, E: float) -> str:
    """Calculate the Rayleigh scattering cross section of an element (barn/atom).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
    """
    try:
        result = xraylib.CSb_Rayl(Z, E)
        return _result_json("CSb_Rayl", result, "barn/atom", {"Z": Z, "E_keV": E})
    except Exception as e:
        return _error_json("CSb_Rayl", e)


@mcp.tool()
def CSb_Compt(Z: int, E: float) -> str:
    """Calculate the Compton scattering cross section of an element (barn/atom).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
    """
    try:
        result = xraylib.CSb_Compt(Z, E)
        return _result_json("CSb_Compt", result, "barn/atom", {"Z": Z, "E_keV": E})
    except Exception as e:
        return _error_json("CSb_Compt", e)


# ---------------------------------------------------------------------------
# Fluorescence line cross-sections
# ---------------------------------------------------------------------------


@mcp.tool()
def CS_FluorLine(Z: int, line: str, E: float) -> str:
    """Calculate the fluorescence line cross section (cm2/g).

    Args:
        Z: Atomic number (1-120)
        line: Line name, e.g. "KL3_LINE", "KA_LINE", "LA1_LINE"
        E: Photon energy in keV
    """
    try:
        line_int = resolve_line(line)
        result = xraylib.CS_FluorLine(Z, line_int, E)
        return _result_json(
            "CS_FluorLine", result, "cm2/g", {"Z": Z, "line": line, "E_keV": E}
        )
    except Exception as e:
        return _error_json("CS_FluorLine", e)


@mcp.tool()
def CSb_FluorLine(Z: int, line: str, E: float) -> str:
    """Calculate the fluorescence line cross section (barn/atom).

    Args:
        Z: Atomic number (1-120)
        line: Line name, e.g. "KL3_LINE", "KA_LINE", "LA1_LINE"
        E: Photon energy in keV
    """
    try:
        line_int = resolve_line(line)
        result = xraylib.CSb_FluorLine(Z, line_int, E)
        return _result_json(
            "CSb_FluorLine", result, "barn/atom", {"Z": Z, "line": line, "E_keV": E}
        )
    except Exception as e:
        return _error_json("CSb_FluorLine", e)


@mcp.tool()
def CS_FluorShell(Z: int, shell: str, E: float) -> str:
    """Calculate the fluorescence shell cross section (cm2/g).

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
        E: Photon energy in keV
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.CS_FluorShell(Z, shell_int, E)
        return _result_json(
            "CS_FluorShell", result, "cm2/g", {"Z": Z, "shell": shell, "E_keV": E}
        )
    except Exception as e:
        return _error_json("CS_FluorShell", e)


@mcp.tool()
def CSb_FluorShell(Z: int, shell: str, E: float) -> str:
    """Calculate the fluorescence shell cross section (barn/atom).

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
        E: Photon energy in keV
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.CSb_FluorShell(Z, shell_int, E)
        return _result_json(
            "CSb_FluorShell",
            result,
            "barn/atom",
            {"Z": Z, "shell": shell, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CSb_FluorShell", e)


# ---------------------------------------------------------------------------
# Kissel fluorescence line cross-sections
# ---------------------------------------------------------------------------


@mcp.tool()
def CS_FluorLine_Kissel(Z: int, line: str, E: float) -> str:
    """Calculate the fluorescence line cross section using Kissel photoionization (cm2/g).

    Args:
        Z: Atomic number (1-120)
        line: Line name, e.g. "KL3_LINE", "KA_LINE"
        E: Photon energy in keV
    """
    try:
        line_int = resolve_line(line)
        result = xraylib.CS_FluorLine_Kissel(Z, line_int, E)
        return _result_json(
            "CS_FluorLine_Kissel",
            result,
            "cm2/g",
            {"Z": Z, "line": line, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CS_FluorLine_Kissel", e)


@mcp.tool()
def CSb_FluorLine_Kissel(Z: int, line: str, E: float) -> str:
    """Calculate the fluorescence line cross section using Kissel photoionization (barn/atom).

    Args:
        Z: Atomic number (1-120)
        line: Line name, e.g. "KL3_LINE", "KA_LINE"
        E: Photon energy in keV
    """
    try:
        line_int = resolve_line(line)
        result = xraylib.CSb_FluorLine_Kissel(Z, line_int, E)
        return _result_json(
            "CSb_FluorLine_Kissel",
            result,
            "barn/atom",
            {"Z": Z, "line": line, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CSb_FluorLine_Kissel", e)


@mcp.tool()
def CS_FluorLine_Kissel_Cascade(Z: int, line: str, E: float) -> str:
    """Calculate the fluorescence line cross section with full cascade using Kissel (cm2/g).

    Args:
        Z: Atomic number (1-120)
        line: Line name, e.g. "KL3_LINE", "KA_LINE"
        E: Photon energy in keV
    """
    try:
        line_int = resolve_line(line)
        result = xraylib.CS_FluorLine_Kissel_Cascade(Z, line_int, E)
        return _result_json(
            "CS_FluorLine_Kissel_Cascade",
            result,
            "cm2/g",
            {"Z": Z, "line": line, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CS_FluorLine_Kissel_Cascade", e)


@mcp.tool()
def CSb_FluorLine_Kissel_Cascade(Z: int, line: str, E: float) -> str:
    """Calculate the fluorescence line cross section with full cascade using Kissel (barn/atom).

    Args:
        Z: Atomic number (1-120)
        line: Line name, e.g. "KL3_LINE", "KA_LINE"
        E: Photon energy in keV
    """
    try:
        line_int = resolve_line(line)
        result = xraylib.CSb_FluorLine_Kissel_Cascade(Z, line_int, E)
        return _result_json(
            "CSb_FluorLine_Kissel_Cascade",
            result,
            "barn/atom",
            {"Z": Z, "line": line, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CSb_FluorLine_Kissel_Cascade", e)


@mcp.tool()
def CS_FluorLine_Kissel_Nonradiative_Cascade(Z: int, line: str, E: float) -> str:
    """Calculate the fluorescence line cross section with nonradiative cascade using Kissel (cm2/g).

    Args:
        Z: Atomic number (1-120)
        line: Line name, e.g. "KL3_LINE", "KA_LINE"
        E: Photon energy in keV
    """
    try:
        line_int = resolve_line(line)
        result = xraylib.CS_FluorLine_Kissel_Nonradiative_Cascade(Z, line_int, E)
        return _result_json(
            "CS_FluorLine_Kissel_Nonradiative_Cascade",
            result,
            "cm2/g",
            {"Z": Z, "line": line, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CS_FluorLine_Kissel_Nonradiative_Cascade", e)


@mcp.tool()
def CSb_FluorLine_Kissel_Nonradiative_Cascade(Z: int, line: str, E: float) -> str:
    """Calculate the fluorescence line cross section with nonradiative cascade using Kissel (barn/atom).

    Args:
        Z: Atomic number (1-120)
        line: Line name, e.g. "KL3_LINE", "KA_LINE"
        E: Photon energy in keV
    """
    try:
        line_int = resolve_line(line)
        result = xraylib.CSb_FluorLine_Kissel_Nonradiative_Cascade(Z, line_int, E)
        return _result_json(
            "CSb_FluorLine_Kissel_Nonradiative_Cascade",
            result,
            "barn/atom",
            {"Z": Z, "line": line, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CSb_FluorLine_Kissel_Nonradiative_Cascade", e)


@mcp.tool()
def CS_FluorLine_Kissel_Radiative_Cascade(Z: int, line: str, E: float) -> str:
    """Calculate the fluorescence line cross section with radiative cascade using Kissel (cm2/g).

    Args:
        Z: Atomic number (1-120)
        line: Line name, e.g. "KL3_LINE", "KA_LINE"
        E: Photon energy in keV
    """
    try:
        line_int = resolve_line(line)
        result = xraylib.CS_FluorLine_Kissel_Radiative_Cascade(Z, line_int, E)
        return _result_json(
            "CS_FluorLine_Kissel_Radiative_Cascade",
            result,
            "cm2/g",
            {"Z": Z, "line": line, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CS_FluorLine_Kissel_Radiative_Cascade", e)


@mcp.tool()
def CSb_FluorLine_Kissel_Radiative_Cascade(Z: int, line: str, E: float) -> str:
    """Calculate the fluorescence line cross section with radiative cascade using Kissel (barn/atom).

    Args:
        Z: Atomic number (1-120)
        line: Line name, e.g. "KL3_LINE", "KA_LINE"
        E: Photon energy in keV
    """
    try:
        line_int = resolve_line(line)
        result = xraylib.CSb_FluorLine_Kissel_Radiative_Cascade(Z, line_int, E)
        return _result_json(
            "CSb_FluorLine_Kissel_Radiative_Cascade",
            result,
            "barn/atom",
            {"Z": Z, "line": line, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CSb_FluorLine_Kissel_Radiative_Cascade", e)


@mcp.tool()
def CS_FluorLine_Kissel_no_Cascade(Z: int, line: str, E: float) -> str:
    """Calculate the fluorescence line cross section without cascade using Kissel (cm2/g).

    Args:
        Z: Atomic number (1-120)
        line: Line name, e.g. "KL3_LINE", "KA_LINE"
        E: Photon energy in keV
    """
    try:
        line_int = resolve_line(line)
        result = xraylib.CS_FluorLine_Kissel_no_Cascade(Z, line_int, E)
        return _result_json(
            "CS_FluorLine_Kissel_no_Cascade",
            result,
            "cm2/g",
            {"Z": Z, "line": line, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CS_FluorLine_Kissel_no_Cascade", e)


@mcp.tool()
def CSb_FluorLine_Kissel_no_Cascade(Z: int, line: str, E: float) -> str:
    """Calculate the fluorescence line cross section without cascade using Kissel (barn/atom).

    Args:
        Z: Atomic number (1-120)
        line: Line name, e.g. "KL3_LINE", "KA_LINE"
        E: Photon energy in keV
    """
    try:
        line_int = resolve_line(line)
        result = xraylib.CSb_FluorLine_Kissel_no_Cascade(Z, line_int, E)
        return _result_json(
            "CSb_FluorLine_Kissel_no_Cascade",
            result,
            "barn/atom",
            {"Z": Z, "line": line, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CSb_FluorLine_Kissel_no_Cascade", e)


# ---------------------------------------------------------------------------
# Kissel fluorescence shell cross-sections
# ---------------------------------------------------------------------------


@mcp.tool()
def CS_FluorShell_Kissel(Z: int, shell: str, E: float) -> str:
    """Calculate the fluorescence shell cross section using Kissel photoionization (cm2/g).

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
        E: Photon energy in keV
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.CS_FluorShell_Kissel(Z, shell_int, E)
        return _result_json(
            "CS_FluorShell_Kissel",
            result,
            "cm2/g",
            {"Z": Z, "shell": shell, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CS_FluorShell_Kissel", e)


@mcp.tool()
def CSb_FluorShell_Kissel(Z: int, shell: str, E: float) -> str:
    """Calculate the fluorescence shell cross section using Kissel photoionization (barn/atom).

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
        E: Photon energy in keV
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.CSb_FluorShell_Kissel(Z, shell_int, E)
        return _result_json(
            "CSb_FluorShell_Kissel",
            result,
            "barn/atom",
            {"Z": Z, "shell": shell, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CSb_FluorShell_Kissel", e)


@mcp.tool()
def CS_FluorShell_Kissel_Cascade(Z: int, shell: str, E: float) -> str:
    """Calculate the fluorescence shell cross section with full cascade using Kissel (cm2/g).

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
        E: Photon energy in keV
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.CS_FluorShell_Kissel_Cascade(Z, shell_int, E)
        return _result_json(
            "CS_FluorShell_Kissel_Cascade",
            result,
            "cm2/g",
            {"Z": Z, "shell": shell, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CS_FluorShell_Kissel_Cascade", e)


@mcp.tool()
def CSb_FluorShell_Kissel_Cascade(Z: int, shell: str, E: float) -> str:
    """Calculate the fluorescence shell cross section with full cascade using Kissel (barn/atom).

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
        E: Photon energy in keV
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.CSb_FluorShell_Kissel_Cascade(Z, shell_int, E)
        return _result_json(
            "CSb_FluorShell_Kissel_Cascade",
            result,
            "barn/atom",
            {"Z": Z, "shell": shell, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CSb_FluorShell_Kissel_Cascade", e)


@mcp.tool()
def CS_FluorShell_Kissel_Nonradiative_Cascade(Z: int, shell: str, E: float) -> str:
    """Calculate the fluorescence shell cross section with nonradiative cascade using Kissel (cm2/g).

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
        E: Photon energy in keV
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.CS_FluorShell_Kissel_Nonradiative_Cascade(Z, shell_int, E)
        return _result_json(
            "CS_FluorShell_Kissel_Nonradiative_Cascade",
            result,
            "cm2/g",
            {"Z": Z, "shell": shell, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CS_FluorShell_Kissel_Nonradiative_Cascade", e)


@mcp.tool()
def CSb_FluorShell_Kissel_Nonradiative_Cascade(Z: int, shell: str, E: float) -> str:
    """Calculate the fluorescence shell cross section with nonradiative cascade using Kissel (barn/atom).

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
        E: Photon energy in keV
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.CSb_FluorShell_Kissel_Nonradiative_Cascade(Z, shell_int, E)
        return _result_json(
            "CSb_FluorShell_Kissel_Nonradiative_Cascade",
            result,
            "barn/atom",
            {"Z": Z, "shell": shell, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CSb_FluorShell_Kissel_Nonradiative_Cascade", e)


@mcp.tool()
def CS_FluorShell_Kissel_Radiative_Cascade(Z: int, shell: str, E: float) -> str:
    """Calculate the fluorescence shell cross section with radiative cascade using Kissel (cm2/g).

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
        E: Photon energy in keV
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.CS_FluorShell_Kissel_Radiative_Cascade(Z, shell_int, E)
        return _result_json(
            "CS_FluorShell_Kissel_Radiative_Cascade",
            result,
            "cm2/g",
            {"Z": Z, "shell": shell, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CS_FluorShell_Kissel_Radiative_Cascade", e)


@mcp.tool()
def CSb_FluorShell_Kissel_Radiative_Cascade(Z: int, shell: str, E: float) -> str:
    """Calculate the fluorescence shell cross section with radiative cascade using Kissel (barn/atom).

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
        E: Photon energy in keV
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.CSb_FluorShell_Kissel_Radiative_Cascade(Z, shell_int, E)
        return _result_json(
            "CSb_FluorShell_Kissel_Radiative_Cascade",
            result,
            "barn/atom",
            {"Z": Z, "shell": shell, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CSb_FluorShell_Kissel_Radiative_Cascade", e)


@mcp.tool()
def CS_FluorShell_Kissel_no_Cascade(Z: int, shell: str, E: float) -> str:
    """Calculate the fluorescence shell cross section without cascade using Kissel (cm2/g).

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
        E: Photon energy in keV
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.CS_FluorShell_Kissel_no_Cascade(Z, shell_int, E)
        return _result_json(
            "CS_FluorShell_Kissel_no_Cascade",
            result,
            "cm2/g",
            {"Z": Z, "shell": shell, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CS_FluorShell_Kissel_no_Cascade", e)


@mcp.tool()
def CSb_FluorShell_Kissel_no_Cascade(Z: int, shell: str, E: float) -> str:
    """Calculate the fluorescence shell cross section without cascade using Kissel (barn/atom).

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
        E: Photon energy in keV
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.CSb_FluorShell_Kissel_no_Cascade(Z, shell_int, E)
        return _result_json(
            "CSb_FluorShell_Kissel_no_Cascade",
            result,
            "barn/atom",
            {"Z": Z, "shell": shell, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CSb_FluorShell_Kissel_no_Cascade", e)


# ---------------------------------------------------------------------------
# Kissel total/photo cross-sections
# ---------------------------------------------------------------------------


@mcp.tool()
def CS_Total_Kissel(Z: int, E: float) -> str:
    """Calculate the total cross section using Kissel photoionization (cm2/g).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
    """
    try:
        result = xraylib.CS_Total_Kissel(Z, E)
        return _result_json("CS_Total_Kissel", result, "cm2/g", {"Z": Z, "E_keV": E})
    except Exception as e:
        return _error_json("CS_Total_Kissel", e)


@mcp.tool()
def CSb_Total_Kissel(Z: int, E: float) -> str:
    """Calculate the total cross section using Kissel photoionization (barn/atom).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
    """
    try:
        result = xraylib.CSb_Total_Kissel(Z, E)
        return _result_json(
            "CSb_Total_Kissel", result, "barn/atom", {"Z": Z, "E_keV": E}
        )
    except Exception as e:
        return _error_json("CSb_Total_Kissel", e)


@mcp.tool()
def CS_Photo_Total(Z: int, E: float) -> str:
    """Calculate the total photoionization cross section using Kissel (cm2/g).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
    """
    try:
        result = xraylib.CS_Photo_Total(Z, E)
        return _result_json("CS_Photo_Total", result, "cm2/g", {"Z": Z, "E_keV": E})
    except Exception as e:
        return _error_json("CS_Photo_Total", e)


@mcp.tool()
def CSb_Photo_Total(Z: int, E: float) -> str:
    """Calculate the total photoionization cross section using Kissel (barn/atom).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
    """
    try:
        result = xraylib.CSb_Photo_Total(Z, E)
        return _result_json(
            "CSb_Photo_Total", result, "barn/atom", {"Z": Z, "E_keV": E}
        )
    except Exception as e:
        return _error_json("CSb_Photo_Total", e)


@mcp.tool()
def CS_Photo_Partial(Z: int, shell: str, E: float) -> str:
    """Calculate the partial photoionization cross section for a shell (cm2/g).

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
        E: Photon energy in keV
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.CS_Photo_Partial(Z, shell_int, E)
        return _result_json(
            "CS_Photo_Partial",
            result,
            "cm2/g",
            {"Z": Z, "shell": shell, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CS_Photo_Partial", e)


@mcp.tool()
def CSb_Photo_Partial(Z: int, shell: str, E: float) -> str:
    """Calculate the partial photoionization cross section for a shell (barn/atom).

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
        E: Photon energy in keV
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.CSb_Photo_Partial(Z, shell_int, E)
        return _result_json(
            "CSb_Photo_Partial",
            result,
            "barn/atom",
            {"Z": Z, "shell": shell, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CSb_Photo_Partial", e)


# ---------------------------------------------------------------------------
# Differential cross-sections
# ---------------------------------------------------------------------------


@mcp.tool()
def DCS_Rayl(Z: int, E: float, theta: float) -> str:
    """Calculate the differential Rayleigh scattering cross section (cm2/g/sr).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
        theta: Scattering polar angle in radians
    """
    try:
        result = xraylib.DCS_Rayl(Z, E, theta)
        return _result_json(
            "DCS_Rayl", result, "cm2/g/sr", {"Z": Z, "E_keV": E, "theta_rad": theta}
        )
    except Exception as e:
        return _error_json("DCS_Rayl", e)


@mcp.tool()
def DCS_Compt(Z: int, E: float, theta: float) -> str:
    """Calculate the differential Compton scattering cross section (cm2/g/sr).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
        theta: Scattering polar angle in radians
    """
    try:
        result = xraylib.DCS_Compt(Z, E, theta)
        return _result_json(
            "DCS_Compt", result, "cm2/g/sr", {"Z": Z, "E_keV": E, "theta_rad": theta}
        )
    except Exception as e:
        return _error_json("DCS_Compt", e)


@mcp.tool()
def DCSb_Rayl(Z: int, E: float, theta: float) -> str:
    """Calculate the differential Rayleigh scattering cross section (barn/atom/sr).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
        theta: Scattering polar angle in radians
    """
    try:
        result = xraylib.DCSb_Rayl(Z, E, theta)
        return _result_json(
            "DCSb_Rayl",
            result,
            "barn/atom/sr",
            {"Z": Z, "E_keV": E, "theta_rad": theta},
        )
    except Exception as e:
        return _error_json("DCSb_Rayl", e)


@mcp.tool()
def DCSb_Compt(Z: int, E: float, theta: float) -> str:
    """Calculate the differential Compton scattering cross section (barn/atom/sr).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
        theta: Scattering polar angle in radians
    """
    try:
        result = xraylib.DCSb_Compt(Z, E, theta)
        return _result_json(
            "DCSb_Compt",
            result,
            "barn/atom/sr",
            {"Z": Z, "E_keV": E, "theta_rad": theta},
        )
    except Exception as e:
        return _error_json("DCSb_Compt", e)


@mcp.tool()
def DCSP_Rayl(Z: int, E: float, theta: float, phi: float) -> str:
    """Calculate the polarized differential Rayleigh scattering cross section (cm2/g/sr).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
        theta: Scattering polar angle in radians
        phi: Scattering azimuthal angle in radians
    """
    try:
        result = xraylib.DCSP_Rayl(Z, E, theta, phi)
        return _result_json(
            "DCSP_Rayl",
            result,
            "cm2/g/sr",
            {"Z": Z, "E_keV": E, "theta_rad": theta, "phi_rad": phi},
        )
    except Exception as e:
        return _error_json("DCSP_Rayl", e)


@mcp.tool()
def DCSP_Compt(Z: int, E: float, theta: float, phi: float) -> str:
    """Calculate the polarized differential Compton scattering cross section (cm2/g/sr).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
        theta: Scattering polar angle in radians
        phi: Scattering azimuthal angle in radians
    """
    try:
        result = xraylib.DCSP_Compt(Z, E, theta, phi)
        return _result_json(
            "DCSP_Compt",
            result,
            "cm2/g/sr",
            {"Z": Z, "E_keV": E, "theta_rad": theta, "phi_rad": phi},
        )
    except Exception as e:
        return _error_json("DCSP_Compt", e)


@mcp.tool()
def DCSPb_Rayl(Z: int, E: float, theta: float, phi: float) -> str:
    """Calculate the polarized differential Rayleigh scattering cross section (barn/atom/sr).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
        theta: Scattering polar angle in radians
        phi: Scattering azimuthal angle in radians
    """
    try:
        result = xraylib.DCSPb_Rayl(Z, E, theta, phi)
        return _result_json(
            "DCSPb_Rayl",
            result,
            "barn/atom/sr",
            {"Z": Z, "E_keV": E, "theta_rad": theta, "phi_rad": phi},
        )
    except Exception as e:
        return _error_json("DCSPb_Rayl", e)


@mcp.tool()
def DCSPb_Compt(Z: int, E: float, theta: float, phi: float) -> str:
    """Calculate the polarized differential Compton scattering cross section (barn/atom/sr).

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
        theta: Scattering polar angle in radians
        phi: Scattering azimuthal angle in radians
    """
    try:
        result = xraylib.DCSPb_Compt(Z, E, theta, phi)
        return _result_json(
            "DCSPb_Compt",
            result,
            "barn/atom/sr",
            {"Z": Z, "E_keV": E, "theta_rad": theta, "phi_rad": phi},
        )
    except Exception as e:
        return _error_json("DCSPb_Compt", e)


# ---------------------------------------------------------------------------
# Scattering factors
# ---------------------------------------------------------------------------


@mcp.tool()
def FF_Rayl(Z: int, q: float) -> str:
    """Calculate the Rayleigh form factor.

    Args:
        Z: Atomic number (1-120)
        q: Momentum transfer in 1/Angstrom
    """
    try:
        result = xraylib.FF_Rayl(Z, q)
        return _result_json("FF_Rayl", result, "", {"Z": Z, "q": q})
    except Exception as e:
        return _error_json("FF_Rayl", e)


@mcp.tool()
def SF_Compt(Z: int, q: float) -> str:
    """Calculate the Compton incoherent scattering function.

    Args:
        Z: Atomic number (1-120)
        q: Momentum transfer in 1/Angstrom
    """
    try:
        result = xraylib.SF_Compt(Z, q)
        return _result_json("SF_Compt", result, "", {"Z": Z, "q": q})
    except Exception as e:
        return _error_json("SF_Compt", e)


@mcp.tool()
def MomentTransf(E: float, theta: float) -> str:
    """Calculate the momentum transfer for X-ray scattering.

    Args:
        E: Photon energy in keV
        theta: Scattering angle in radians
    """
    try:
        result = xraylib.MomentTransf(E, theta)
        return _result_json(
            "MomentTransf", result, "1/Angstrom", {"E_keV": E, "theta_rad": theta}
        )
    except Exception as e:
        return _error_json("MomentTransf", e)


@mcp.tool()
def ComptonEnergy(E0: float, theta: float) -> str:
    """Calculate the photon energy after Compton scattering.

    Args:
        E0: Incident photon energy in keV
        theta: Scattering angle in radians
    """
    try:
        result = xraylib.ComptonEnergy(E0, theta)
        return _result_json(
            "ComptonEnergy", result, "keV", {"E0_keV": E0, "theta_rad": theta}
        )
    except Exception as e:
        return _error_json("ComptonEnergy", e)


@mcp.tool()
def Fi(Z: int, E: float) -> str:
    """Calculate the real part of the anomalous scattering factor (delta f').

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
    """
    try:
        result = xraylib.Fi(Z, E)
        return _result_json("Fi", result, "electrons", {"Z": Z, "E_keV": E})
    except Exception as e:
        return _error_json("Fi", e)


@mcp.tool()
def Fii(Z: int, E: float) -> str:
    """Calculate the imaginary part of the anomalous scattering factor (delta f'').

    Args:
        Z: Atomic number (1-120)
        E: Photon energy in keV
    """
    try:
        result = xraylib.Fii(Z, E)
        return _result_json("Fii", result, "electrons", {"Z": Z, "E_keV": E})
    except Exception as e:
        return _error_json("Fii", e)


@mcp.tool()
def ComptonProfile(Z: int, pz: float) -> str:
    """Calculate the Compton profile for an element.

    Args:
        Z: Atomic number (1-120)
        pz: Projection of the electron momentum in atomic units
    """
    try:
        result = xraylib.ComptonProfile(Z, pz)
        return _result_json("ComptonProfile", result, "", {"Z": Z, "pz": pz})
    except Exception as e:
        return _error_json("ComptonProfile", e)


@mcp.tool()
def ComptonProfile_Partial(Z: int, shell: str, pz: float) -> str:
    """Calculate the partial Compton profile for a shell of an element.

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
        pz: Projection of the electron momentum in atomic units
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.ComptonProfile_Partial(Z, shell_int, pz)
        return _result_json(
            "ComptonProfile_Partial",
            result,
            "",
            {"Z": Z, "shell": shell, "pz": pz},
        )
    except Exception as e:
        return _error_json("ComptonProfile_Partial", e)


# ---------------------------------------------------------------------------
# Auger and Coster-Kronig transitions
# ---------------------------------------------------------------------------


@mcp.tool()
def AugerRate(Z: int, auger_trans: str) -> str:
    """Get the Auger rate for a given transition.

    Args:
        Z: Atomic number (1-120)
        auger_trans: Auger transition name, e.g. "K_L1L1_AUGER", "L2_M5M5_AUGER"
    """
    try:
        auger_int = resolve_auger(auger_trans)
        result = xraylib.AugerRate(Z, auger_int)
        return _result_json(
            "AugerRate", result, "", {"Z": Z, "auger_trans": auger_trans}
        )
    except Exception as e:
        return _error_json("AugerRate", e)


@mcp.tool()
def AugerYield(Z: int, shell: str) -> str:
    """Get the Auger yield for a given shell.

    Args:
        Z: Atomic number (1-120)
        shell: Shell name, e.g. "K_SHELL", "L1_SHELL"
    """
    try:
        shell_int = resolve_shell(shell)
        result = xraylib.AugerYield(Z, shell_int)
        return _result_json("AugerYield", result, "", {"Z": Z, "shell": shell})
    except Exception as e:
        return _error_json("AugerYield", e)


@mcp.tool()
def CosKronTransProb(Z: int, trans: str) -> str:
    """Get the Coster-Kronig transition probability.

    Args:
        Z: Atomic number (1-120)
        trans: Transition name, e.g. "FL13_TRANS", "FM15_TRANS"
    """
    try:
        trans_int = resolve_transition(trans)
        result = xraylib.CosKronTransProb(Z, trans_int)
        return _result_json("CosKronTransProb", result, "", {"Z": Z, "trans": trans})
    except Exception as e:
        return _error_json("CosKronTransProb", e)


# ---------------------------------------------------------------------------
# Compound cross-sections (cm2/g)
# ---------------------------------------------------------------------------


@mcp.tool()
def CS_Total_CP(compound: str, E: float) -> str:
    """Calculate the total cross section of a compound (cm2/g).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O", "CaCO3"
        E: Photon energy in keV
    """
    try:
        result = xraylib.CS_Total_CP(compound, E)
        return _result_json(
            "CS_Total_CP", result, "cm2/g", {"compound": compound, "E_keV": E}
        )
    except Exception as e:
        return _error_json("CS_Total_CP", e)


@mcp.tool()
def CS_Photo_CP(compound: str, E: float) -> str:
    """Calculate the photoionization cross section of a compound (cm2/g).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
    """
    try:
        result = xraylib.CS_Photo_CP(compound, E)
        return _result_json(
            "CS_Photo_CP", result, "cm2/g", {"compound": compound, "E_keV": E}
        )
    except Exception as e:
        return _error_json("CS_Photo_CP", e)


@mcp.tool()
def CS_Rayl_CP(compound: str, E: float) -> str:
    """Calculate the Rayleigh scattering cross section of a compound (cm2/g).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
    """
    try:
        result = xraylib.CS_Rayl_CP(compound, E)
        return _result_json(
            "CS_Rayl_CP", result, "cm2/g", {"compound": compound, "E_keV": E}
        )
    except Exception as e:
        return _error_json("CS_Rayl_CP", e)


@mcp.tool()
def CS_Compt_CP(compound: str, E: float) -> str:
    """Calculate the Compton scattering cross section of a compound (cm2/g).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
    """
    try:
        result = xraylib.CS_Compt_CP(compound, E)
        return _result_json(
            "CS_Compt_CP", result, "cm2/g", {"compound": compound, "E_keV": E}
        )
    except Exception as e:
        return _error_json("CS_Compt_CP", e)


@mcp.tool()
def CS_Energy_CP(compound: str, E: float) -> str:
    """Calculate the mass energy-absorption cross section of a compound (cm2/g).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
    """
    try:
        result = xraylib.CS_Energy_CP(compound, E)
        return _result_json(
            "CS_Energy_CP", result, "cm2/g", {"compound": compound, "E_keV": E}
        )
    except Exception as e:
        return _error_json("CS_Energy_CP", e)


@mcp.tool()
def CS_Total_Kissel_CP(compound: str, E: float) -> str:
    """Calculate the total cross section of a compound using Kissel photoionization (cm2/g).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
    """
    try:
        result = xraylib.CS_Total_Kissel_CP(compound, E)
        return _result_json(
            "CS_Total_Kissel_CP",
            result,
            "cm2/g",
            {"compound": compound, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CS_Total_Kissel_CP", e)


@mcp.tool()
def CS_Photo_Total_CP(compound: str, E: float) -> str:
    """Calculate the total photoionization cross section of a compound using Kissel (cm2/g).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
    """
    try:
        result = xraylib.CS_Photo_Total_CP(compound, E)
        return _result_json(
            "CS_Photo_Total_CP",
            result,
            "cm2/g",
            {"compound": compound, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CS_Photo_Total_CP", e)


# ---------------------------------------------------------------------------
# Compound cross-sections (barn/atom)
# ---------------------------------------------------------------------------


@mcp.tool()
def CSb_Total_CP(compound: str, E: float) -> str:
    """Calculate the total cross section of a compound (barn/atom).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
    """
    try:
        result = xraylib.CSb_Total_CP(compound, E)
        return _result_json(
            "CSb_Total_CP", result, "barn/atom", {"compound": compound, "E_keV": E}
        )
    except Exception as e:
        return _error_json("CSb_Total_CP", e)


@mcp.tool()
def CSb_Photo_CP(compound: str, E: float) -> str:
    """Calculate the photoionization cross section of a compound (barn/atom).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
    """
    try:
        result = xraylib.CSb_Photo_CP(compound, E)
        return _result_json(
            "CSb_Photo_CP", result, "barn/atom", {"compound": compound, "E_keV": E}
        )
    except Exception as e:
        return _error_json("CSb_Photo_CP", e)


@mcp.tool()
def CSb_Rayl_CP(compound: str, E: float) -> str:
    """Calculate the Rayleigh scattering cross section of a compound (barn/atom).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
    """
    try:
        result = xraylib.CSb_Rayl_CP(compound, E)
        return _result_json(
            "CSb_Rayl_CP", result, "barn/atom", {"compound": compound, "E_keV": E}
        )
    except Exception as e:
        return _error_json("CSb_Rayl_CP", e)


@mcp.tool()
def CSb_Compt_CP(compound: str, E: float) -> str:
    """Calculate the Compton scattering cross section of a compound (barn/atom).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
    """
    try:
        result = xraylib.CSb_Compt_CP(compound, E)
        return _result_json(
            "CSb_Compt_CP", result, "barn/atom", {"compound": compound, "E_keV": E}
        )
    except Exception as e:
        return _error_json("CSb_Compt_CP", e)


@mcp.tool()
def CSb_Total_Kissel_CP(compound: str, E: float) -> str:
    """Calculate the total cross section of a compound using Kissel photoionization (barn/atom).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
    """
    try:
        result = xraylib.CSb_Total_Kissel_CP(compound, E)
        return _result_json(
            "CSb_Total_Kissel_CP",
            result,
            "barn/atom",
            {"compound": compound, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CSb_Total_Kissel_CP", e)


@mcp.tool()
def CSb_Photo_Total_CP(compound: str, E: float) -> str:
    """Calculate the total photoionization cross section of a compound using Kissel (barn/atom).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
    """
    try:
        result = xraylib.CSb_Photo_Total_CP(compound, E)
        return _result_json(
            "CSb_Photo_Total_CP",
            result,
            "barn/atom",
            {"compound": compound, "E_keV": E},
        )
    except Exception as e:
        return _error_json("CSb_Photo_Total_CP", e)


# ---------------------------------------------------------------------------
# Compound differential cross-sections
# ---------------------------------------------------------------------------


@mcp.tool()
def DCS_Rayl_CP(compound: str, E: float, theta: float) -> str:
    """Calculate the differential Rayleigh scattering cross section of a compound (cm2/g/sr).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
        theta: Scattering polar angle in radians
    """
    try:
        result = xraylib.DCS_Rayl_CP(compound, E, theta)
        return _result_json(
            "DCS_Rayl_CP",
            result,
            "cm2/g/sr",
            {"compound": compound, "E_keV": E, "theta_rad": theta},
        )
    except Exception as e:
        return _error_json("DCS_Rayl_CP", e)


@mcp.tool()
def DCS_Compt_CP(compound: str, E: float, theta: float) -> str:
    """Calculate the differential Compton scattering cross section of a compound (cm2/g/sr).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
        theta: Scattering polar angle in radians
    """
    try:
        result = xraylib.DCS_Compt_CP(compound, E, theta)
        return _result_json(
            "DCS_Compt_CP",
            result,
            "cm2/g/sr",
            {"compound": compound, "E_keV": E, "theta_rad": theta},
        )
    except Exception as e:
        return _error_json("DCS_Compt_CP", e)


@mcp.tool()
def DCSb_Rayl_CP(compound: str, E: float, theta: float) -> str:
    """Calculate the differential Rayleigh scattering cross section of a compound (barn/atom/sr).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
        theta: Scattering polar angle in radians
    """
    try:
        result = xraylib.DCSb_Rayl_CP(compound, E, theta)
        return _result_json(
            "DCSb_Rayl_CP",
            result,
            "barn/atom/sr",
            {"compound": compound, "E_keV": E, "theta_rad": theta},
        )
    except Exception as e:
        return _error_json("DCSb_Rayl_CP", e)


@mcp.tool()
def DCSb_Compt_CP(compound: str, E: float, theta: float) -> str:
    """Calculate the differential Compton scattering cross section of a compound (barn/atom/sr).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
        theta: Scattering polar angle in radians
    """
    try:
        result = xraylib.DCSb_Compt_CP(compound, E, theta)
        return _result_json(
            "DCSb_Compt_CP",
            result,
            "barn/atom/sr",
            {"compound": compound, "E_keV": E, "theta_rad": theta},
        )
    except Exception as e:
        return _error_json("DCSb_Compt_CP", e)


@mcp.tool()
def DCSP_Rayl_CP(compound: str, E: float, theta: float, phi: float) -> str:
    """Calculate the polarized differential Rayleigh scattering cross section of a compound (cm2/g/sr).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
        theta: Scattering polar angle in radians
        phi: Scattering azimuthal angle in radians
    """
    try:
        result = xraylib.DCSP_Rayl_CP(compound, E, theta, phi)
        return _result_json(
            "DCSP_Rayl_CP",
            result,
            "cm2/g/sr",
            {"compound": compound, "E_keV": E, "theta_rad": theta, "phi_rad": phi},
        )
    except Exception as e:
        return _error_json("DCSP_Rayl_CP", e)


@mcp.tool()
def DCSP_Compt_CP(compound: str, E: float, theta: float, phi: float) -> str:
    """Calculate the polarized differential Compton scattering cross section of a compound (cm2/g/sr).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
        theta: Scattering polar angle in radians
        phi: Scattering azimuthal angle in radians
    """
    try:
        result = xraylib.DCSP_Compt_CP(compound, E, theta, phi)
        return _result_json(
            "DCSP_Compt_CP",
            result,
            "cm2/g/sr",
            {"compound": compound, "E_keV": E, "theta_rad": theta, "phi_rad": phi},
        )
    except Exception as e:
        return _error_json("DCSP_Compt_CP", e)


@mcp.tool()
def DCSPb_Rayl_CP(compound: str, E: float, theta: float, phi: float) -> str:
    """Calculate the polarized differential Rayleigh scattering cross section of a compound (barn/atom/sr).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
        theta: Scattering polar angle in radians
        phi: Scattering azimuthal angle in radians
    """
    try:
        result = xraylib.DCSPb_Rayl_CP(compound, E, theta, phi)
        return _result_json(
            "DCSPb_Rayl_CP",
            result,
            "barn/atom/sr",
            {"compound": compound, "E_keV": E, "theta_rad": theta, "phi_rad": phi},
        )
    except Exception as e:
        return _error_json("DCSPb_Rayl_CP", e)


@mcp.tool()
def DCSPb_Compt_CP(compound: str, E: float, theta: float, phi: float) -> str:
    """Calculate the polarized differential Compton scattering cross section of a compound (barn/atom/sr).

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
        theta: Scattering polar angle in radians
        phi: Scattering azimuthal angle in radians
    """
    try:
        result = xraylib.DCSPb_Compt_CP(compound, E, theta, phi)
        return _result_json(
            "DCSPb_Compt_CP",
            result,
            "barn/atom/sr",
            {"compound": compound, "E_keV": E, "theta_rad": theta, "phi_rad": phi},
        )
    except Exception as e:
        return _error_json("DCSPb_Compt_CP", e)


# ---------------------------------------------------------------------------
# Refractive index
# ---------------------------------------------------------------------------


@mcp.tool()
def Refractive_Index_Re(compound: str, E: float, density: float) -> str:
    """Calculate the real part of the refractive index of a compound.

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
        density: Density in g/cm3
    """
    try:
        result = xraylib.Refractive_Index_Re(compound, E, density)
        return _result_json(
            "Refractive_Index_Re",
            result,
            "",
            {"compound": compound, "E_keV": E, "density_g_cm3": density},
        )
    except Exception as e:
        return _error_json("Refractive_Index_Re", e)


@mcp.tool()
def Refractive_Index_Im(compound: str, E: float, density: float) -> str:
    """Calculate the imaginary part of the refractive index of a compound.

    Args:
        compound: Chemical formula, e.g. "SiO2", "H2O"
        E: Photon energy in keV
        density: Density in g/cm3
    """
    try:
        result = xraylib.Refractive_Index_Im(compound, E, density)
        return _result_json(
            "Refractive_Index_Im",
            result,
            "",
            {"compound": compound, "E_keV": E, "density_g_cm3": density},
        )
    except Exception as e:
        return _error_json("Refractive_Index_Im", e)


# ---------------------------------------------------------------------------
# NIST compounds
# ---------------------------------------------------------------------------


@mcp.tool()
def GetCompoundDataNISTByName(name: str) -> str:
    """Get NIST compound data by compound name.

    Args:
        name: NIST compound name, e.g. "Water, Liquid", "Air, Dry (near sea level)"
    """
    try:
        result = xraylib.GetCompoundDataNISTByName(name)
        data = {
            "name": result["name"],
            "nElements": result["nElements"],
            "Elements": result["Elements"],
            "massFractions": result["massFractions"],
            "density": result["density"],
        }
        return _result_json("GetCompoundDataNISTByName", data, "", {"name": name})
    except Exception as e:
        return _error_json("GetCompoundDataNISTByName", e)


@mcp.tool()
def GetCompoundDataNISTByIndex(index: int) -> str:
    """Get NIST compound data by index number.

    Args:
        index: NIST compound index (0-based)
    """
    try:
        result = xraylib.GetCompoundDataNISTByIndex(index)
        data = {
            "name": result["name"],
            "nElements": result["nElements"],
            "Elements": result["Elements"],
            "massFractions": result["massFractions"],
            "density": result["density"],
        }
        return _result_json("GetCompoundDataNISTByIndex", data, "", {"index": index})
    except Exception as e:
        return _error_json("GetCompoundDataNISTByIndex", e)


@mcp.tool()
def GetCompoundDataNISTList() -> str:
    """Get the list of all available NIST compound names."""
    try:
        result = xraylib.GetCompoundDataNISTList()
        return _result_json("GetCompoundDataNISTList", result, "", {})
    except Exception as e:
        return _error_json("GetCompoundDataNISTList", e)


# ---------------------------------------------------------------------------
# Radionuclide data tools


@mcp.tool()
def GetRadioNuclideDataByName(name: str) -> str:
    """Get radionuclide data by name.

    Args:
        name: Radionuclide name, e.g. "55Fe", "241Am", "109Cd"
    """
    try:
        result = xraylib.GetRadioNuclideDataByName(name)
        data = {
            "name": result["name"],
            "Z": result["Z"],
            "A": result["A"],
            "N": result["N"],
            "Z_xray": result["Z_xray"],
            "nXrays": result["nXrays"],
            "nGammas": result["nGammas"],
            "XrayLines": list(result["XrayLines"]),
            "XrayIntensities": list(result["XrayIntensities"]),
            "GammaEnergies": list(result["GammaEnergies"]),
            "GammaIntensities": list(result["GammaIntensities"]),
        }
        return _result_json("GetRadioNuclideDataByName", data, "", {"name": name})
    except Exception as e:
        return _error_json("GetRadioNuclideDataByName", e)


@mcp.tool()
def GetRadioNuclideDataByIndex(index: int) -> str:
    """Get radionuclide data by index number.

    Args:
        index: Radionuclide index (0-based)
    """
    try:
        result = xraylib.GetRadioNuclideDataByIndex(index)
        data = {
            "name": result["name"],
            "Z": result["Z"],
            "A": result["A"],
            "N": result["N"],
            "Z_xray": result["Z_xray"],
            "nXrays": result["nXrays"],
            "nGammas": result["nGammas"],
            "XrayLines": list(result["XrayLines"]),
            "XrayIntensities": list(result["XrayIntensities"]),
            "GammaEnergies": list(result["GammaEnergies"]),
            "GammaIntensities": list(result["GammaIntensities"]),
        }
        return _result_json("GetRadioNuclideDataByIndex", data, "", {"index": index})
    except Exception as e:
        return _error_json("GetRadioNuclideDataByIndex", e)


@mcp.tool()
def GetRadioNuclideDataList() -> str:
    """Get the list of all available radionuclide names."""
    try:
        result = xraylib.GetRadioNuclideDataList()
        return _result_json("GetRadioNuclideDataList", list(result), "", {})
    except Exception as e:
        return _error_json("GetRadioNuclideDataList", e)


# ---------------------------------------------------------------------------
# Constant listing tools
# ---------------------------------------------------------------------------


@mcp.tool()
def ListLineConstants() -> str:
    """List all available X-ray fluorescence line constant names."""
    try:
        return _result_json("ListLineConstants", list_lines(), "", {})
    except Exception as e:
        return _error_json("ListLineConstants", e)


@mcp.tool()
def ListShellConstants() -> str:
    """List all available shell constant names."""
    try:
        return _result_json("ListShellConstants", list_shells(), "", {})
    except Exception as e:
        return _error_json("ListShellConstants", e)


@mcp.tool()
def ListTransitionConstants() -> str:
    """List all available Coster-Kronig transition constant names."""
    try:
        return _result_json("ListTransitionConstants", list_transitions(), "", {})
    except Exception as e:
        return _error_json("ListTransitionConstants", e)


@mcp.tool()
def ListAugerConstants() -> str:
    """List all available Auger transition constant names."""
    try:
        return _result_json("ListAugerConstants", list_auger_transitions(), "", {})
    except Exception as e:
        return _error_json("ListAugerConstants", e)


@mcp.tool()
def ListNISTCompoundConstants() -> str:
    """List all available NIST compound constant names."""
    try:
        return _result_json("ListNISTCompoundConstants", list_nist_compounds(), "", {})
    except Exception as e:
        return _error_json("ListNISTCompoundConstants", e)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the xraylib MCP server."""
    parser = argparse.ArgumentParser(description="xraylib MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport=args.transport)


if __name__ == "__main__":  # pragma: no cover
    main()
