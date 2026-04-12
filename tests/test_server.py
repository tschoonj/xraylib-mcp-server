"""Tests for xraylib_mcp.server tool functions.

Each tool returns a JSON string. We call the functions directly (they are
plain synchronous functions despite being registered as MCP tools) and
parse the JSON to verify structure and values.
"""

from __future__ import annotations

import json
import math
from unittest.mock import patch

import pytest
import xraylib

from xraylib_mcp_server.server import (
    Atomic_Factors,
    AtomicLevelWidth,
    AtomicNumberToSymbol,
    AtomicWeight,
    AugerRate,
    AugerYield,
    CompoundParser,
    ComptonEnergy,
    ComptonProfile,
    ComptonProfile_Partial,
    CosKronTransProb,
    CS_Compt,
    CS_Compt_CP,
    CS_Energy,
    CS_Energy_CP,
    CS_FluorLine,
    CS_FluorLine_Kissel,
    CS_FluorLine_Kissel_Cascade,
    CS_FluorLine_Kissel_no_Cascade,
    CS_FluorLine_Kissel_Nonradiative_Cascade,
    CS_FluorLine_Kissel_Radiative_Cascade,
    CS_FluorShell,
    CS_FluorShell_Kissel,
    CS_FluorShell_Kissel_Cascade,
    CS_FluorShell_Kissel_no_Cascade,
    CS_FluorShell_Kissel_Nonradiative_Cascade,
    CS_FluorShell_Kissel_Radiative_Cascade,
    CS_KN,
    CS_Photo,
    CS_Photo_CP,
    CS_Photo_Partial,
    CS_Photo_Total,
    CS_Photo_Total_CP,
    CS_Rayl,
    CS_Rayl_CP,
    CS_Total,
    CS_Total_CP,
    CS_Total_Kissel,
    CS_Total_Kissel_CP,
    CSb_Compt,
    CSb_Compt_CP,
    CSb_FluorLine,
    CSb_FluorLine_Kissel,
    CSb_FluorLine_Kissel_Cascade,
    CSb_FluorLine_Kissel_no_Cascade,
    CSb_FluorLine_Kissel_Nonradiative_Cascade,
    CSb_FluorLine_Kissel_Radiative_Cascade,
    CSb_FluorShell,
    CSb_FluorShell_Kissel,
    CSb_FluorShell_Kissel_Cascade,
    CSb_FluorShell_Kissel_no_Cascade,
    CSb_FluorShell_Kissel_Nonradiative_Cascade,
    CSb_FluorShell_Kissel_Radiative_Cascade,
    CSb_Photo,
    CSb_Photo_CP,
    CSb_Photo_Partial,
    CSb_Photo_Total,
    CSb_Photo_Total_CP,
    CSb_Rayl,
    CSb_Rayl_CP,
    CSb_Total,
    CSb_Total_CP,
    CSb_Total_Kissel,
    CSb_Total_Kissel_CP,
    DCS_Compt,
    DCS_Compt_CP,
    DCS_Rayl,
    DCS_Rayl_CP,
    DCSb_Compt,
    DCSb_Compt_CP,
    DCSb_Rayl,
    DCSb_Rayl_CP,
    DCSP_Compt,
    DCSP_Compt_CP,
    DCSP_Rayl,
    DCSP_Rayl_CP,
    DCSPb_Compt,
    DCSPb_Compt_CP,
    DCSPb_Rayl,
    DCSPb_Rayl_CP,
    EdgeEnergy,
    ElectronConfig,
    ElementDensity,
    FF_Rayl,
    Fi,
    Fii,
    FluorYield,
    GetCompoundDataNISTByIndex,
    GetCompoundDataNISTByName,
    GetCompoundDataNISTList,
    JumpFactor,
    LineEnergy,
    ListAugerConstants,
    ListLineConstants,
    ListNISTCompoundConstants,
    ListShellConstants,
    ListTransitionConstants,
    MomentTransf,
    RadRate,
    Refractive_Index_Im,
    Refractive_Index_Re,
    SF_Compt,
    SymbolToAtomicNumber,
    _error_json,
    _result_json,
    main,
    mcp,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse(raw: str) -> dict:
    """Parse tool JSON output."""
    return json.loads(raw)


def _assert_success(data: dict, func_name: str) -> None:
    """Assert that a tool result is successful (no error key)."""
    assert "error" not in data, f"Unexpected error: {data.get('error')}"
    assert data["function"] == func_name


def _assert_error(data: dict, func_name: str) -> None:
    """Assert that a tool result is an error."""
    assert "error" in data
    assert data["function"] == func_name


# ---------------------------------------------------------------------------
# _result_json / _error_json
# ---------------------------------------------------------------------------


class TestResultJson:
    def test_basic(self):
        raw = _result_json("foo", 42.0, "keV", {"Z": 26})
        data = json.loads(raw)
        assert data["function"] == "foo"
        assert data["result"] == 42.0
        assert data["units"] == "keV"
        assert data["inputs"] == {"Z": 26}

    def test_empty_units(self):
        data = json.loads(_result_json("bar", 1.0, "", {}))
        assert data["units"] == ""


class TestErrorJson:
    def test_basic(self):
        raw = _error_json("foo", ValueError("bad input"))
        data = json.loads(raw)
        assert data["function"] == "foo"
        assert "bad input" in data["error"]


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


class TestMain:
    def test_stdio_default(self):
        with patch.object(mcp, "run") as mock_run, \
             patch("sys.argv", ["xraylib-mcp-server"]):
            main()
            mock_run.assert_called_once_with()

    def test_http_transport(self):
        with patch.object(mcp, "run") as mock_run, \
             patch("sys.argv", [
                 "xraylib-mcp-server",
                 "--transport", "http",
                 "--host", "localhost",
                 "--port", "9000",
             ]):
            main()
            mock_run.assert_called_once_with(
                transport="http", host="localhost", port=9000,
            )

    def test_sse_transport(self):
        with patch.object(mcp, "run") as mock_run, \
             patch("sys.argv", [
                 "xraylib-mcp-server",
                 "--transport", "sse",
             ]):
            main()
            mock_run.assert_called_once_with(
                transport="sse", host="0.0.0.0", port=8000,
            )


# ---------------------------------------------------------------------------
# Utility tools
# ---------------------------------------------------------------------------


class TestAtomicNumberToSymbol:
    def test_iron(self):
        data = _parse(AtomicNumberToSymbol(26))
        _assert_success(data, "AtomicNumberToSymbol")
        assert data["result"] == "Fe"

    def test_hydrogen(self):
        data = _parse(AtomicNumberToSymbol(1))
        _assert_success(data, "AtomicNumberToSymbol")
        assert data["result"] == "H"

    def test_invalid_z(self):
        data = _parse(AtomicNumberToSymbol(0))
        _assert_error(data, "AtomicNumberToSymbol")


class TestSymbolToAtomicNumber:
    def test_iron(self):
        data = _parse(SymbolToAtomicNumber("Fe"))
        _assert_success(data, "SymbolToAtomicNumber")
        assert data["result"] == 26

    def test_invalid_symbol(self):
        data = _parse(SymbolToAtomicNumber("Xx"))
        _assert_error(data, "SymbolToAtomicNumber")


class TestAtomicWeight:
    def test_iron(self):
        data = _parse(AtomicWeight(26))
        _assert_success(data, "AtomicWeight")
        assert data["units"] == "g/mol"
        assert data["result"] == pytest.approx(55.845, rel=1e-3)

    def test_invalid_z(self):
        data = _parse(AtomicWeight(0))
        _assert_error(data, "AtomicWeight")


class TestElementDensity:
    def test_iron(self):
        data = _parse(ElementDensity(26))
        _assert_success(data, "ElementDensity")
        assert data["units"] == "g/cm3"
        assert data["result"] > 0

    def test_invalid_z(self):
        data = _parse(ElementDensity(0))
        _assert_error(data, "ElementDensity")


class TestElectronConfig:
    def test_fe_k_shell(self):
        data = _parse(ElectronConfig(26, "K_SHELL"))
        _assert_success(data, "ElectronConfig")
        assert data["result"] == pytest.approx(2.0)

    def test_invalid_shell_name(self):
        data = _parse(ElectronConfig(26, "FAKE_SHELL"))
        _assert_error(data, "ElectronConfig")


class TestCompoundParser:
    def test_water(self):
        data = _parse(CompoundParser("H2O"))
        _assert_success(data, "CompoundParser")
        assert data["result"]["nElements"] == 2

    def test_invalid_formula(self):
        data = _parse(CompoundParser("XxYy123"))
        _assert_error(data, "CompoundParser")


class TestAtomicFactors:
    def test_fe(self):
        data = _parse(Atomic_Factors(26, 10.0, 0.5, 1.0))
        _assert_success(data, "Atomic_Factors")
        assert "f0" in data["result"]
        assert "f_prime" in data["result"]
        assert "f_prime2" in data["result"]

    def test_invalid_z(self):
        data = _parse(Atomic_Factors(0, 10.0, 0.5, 1.0))
        _assert_error(data, "Atomic_Factors")


# ---------------------------------------------------------------------------
# Line/edge/shell properties
# ---------------------------------------------------------------------------


class TestLineEnergy:
    def test_fe_ka(self):
        data = _parse(LineEnergy(26, "KA_LINE"))
        _assert_success(data, "LineEnergy")
        assert data["units"] == "keV"
        assert data["result"] == pytest.approx(
            xraylib.LineEnergy(26, xraylib.KA_LINE), rel=1e-6
        )

    def test_invalid_line(self):
        data = _parse(LineEnergy(26, "BOGUS"))
        _assert_error(data, "LineEnergy")


class TestEdgeEnergy:
    def test_fe_k(self):
        data = _parse(EdgeEnergy(26, "K_SHELL"))
        _assert_success(data, "EdgeEnergy")
        assert data["units"] == "keV"
        assert data["result"] == pytest.approx(
            xraylib.EdgeEnergy(26, xraylib.K_SHELL), rel=1e-6
        )

    def test_invalid_shell(self):
        data = _parse(EdgeEnergy(26, "FAKE"))
        _assert_error(data, "EdgeEnergy")


class TestFluorYield:
    def test_fe_k(self):
        data = _parse(FluorYield(26, "K_SHELL"))
        _assert_success(data, "FluorYield")
        assert 0 < data["result"] < 1

    def test_invalid_shell(self):
        data = _parse(FluorYield(26, "FAKE"))
        _assert_error(data, "FluorYield")


class TestJumpFactor:
    def test_fe_k(self):
        data = _parse(JumpFactor(26, "K_SHELL"))
        _assert_success(data, "JumpFactor")
        assert data["result"] > 1

    def test_invalid_shell(self):
        data = _parse(JumpFactor(26, "FAKE"))
        _assert_error(data, "JumpFactor")


class TestRadRate:
    def test_fe_kl3(self):
        data = _parse(RadRate(26, "KL3_LINE"))
        _assert_success(data, "RadRate")
        assert 0 < data["result"] <= 1

    def test_invalid_line(self):
        data = _parse(RadRate(26, "FAKE"))
        _assert_error(data, "RadRate")


class TestAtomicLevelWidth:
    def test_fe_k(self):
        data = _parse(AtomicLevelWidth(26, "K_SHELL"))
        _assert_success(data, "AtomicLevelWidth")
        assert data["units"] == "keV"
        assert data["result"] > 0

    def test_invalid_shell(self):
        data = _parse(AtomicLevelWidth(26, "FAKE"))
        _assert_error(data, "AtomicLevelWidth")


# ---------------------------------------------------------------------------
# Element cross-sections (cm2/g) — success + error
# ---------------------------------------------------------------------------


class TestCSTotal:
    def test_fe_10kev(self):
        data = _parse(CS_Total(26, 10.0))
        _assert_success(data, "CS_Total")
        assert data["units"] == "cm2/g"
        assert data["result"] == pytest.approx(
            xraylib.CS_Total(26, 10.0), rel=1e-6
        )

    def test_invalid_energy(self):
        data = _parse(CS_Total(26, 0.0))
        _assert_error(data, "CS_Total")


class TestCSPhoto:
    def test_fe_10kev(self):
        data = _parse(CS_Photo(26, 10.0))
        _assert_success(data, "CS_Photo")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_Photo(0, 10.0))
        _assert_error(data, "CS_Photo")


class TestCSRayl:
    def test_fe_10kev(self):
        data = _parse(CS_Rayl(26, 10.0))
        _assert_success(data, "CS_Rayl")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_Rayl(0, 10.0))
        _assert_error(data, "CS_Rayl")


class TestCSCompt:
    def test_fe_10kev(self):
        data = _parse(CS_Compt(26, 10.0))
        _assert_success(data, "CS_Compt")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_Compt(0, 10.0))
        _assert_error(data, "CS_Compt")


class TestCSKN:
    def test_10kev(self):
        data = _parse(CS_KN(10.0))
        _assert_success(data, "CS_KN")
        assert data["units"] == "barn/electron"
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_KN(0.0))
        _assert_error(data, "CS_KN")


class TestCSEnergy:
    def test_fe_10kev(self):
        data = _parse(CS_Energy(26, 10.0))
        _assert_success(data, "CS_Energy")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_Energy(0, 10.0))
        _assert_error(data, "CS_Energy")


# ---------------------------------------------------------------------------
# Element cross-sections (barn/atom) — success + error
# ---------------------------------------------------------------------------


class TestCSbTotal:
    def test_fe_10kev(self):
        data = _parse(CSb_Total(26, 10.0))
        _assert_success(data, "CSb_Total")
        assert data["units"] == "barn/atom"
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CSb_Total(0, 10.0))
        _assert_error(data, "CSb_Total")


class TestCSbPhoto:
    def test_fe_10kev(self):
        data = _parse(CSb_Photo(26, 10.0))
        _assert_success(data, "CSb_Photo")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CSb_Photo(0, 10.0))
        _assert_error(data, "CSb_Photo")


class TestCSbRayl:
    def test_fe_10kev(self):
        data = _parse(CSb_Rayl(26, 10.0))
        _assert_success(data, "CSb_Rayl")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CSb_Rayl(0, 10.0))
        _assert_error(data, "CSb_Rayl")


class TestCSbCompt:
    def test_fe_10kev(self):
        data = _parse(CSb_Compt(26, 10.0))
        _assert_success(data, "CSb_Compt")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CSb_Compt(0, 10.0))
        _assert_error(data, "CSb_Compt")


# ---------------------------------------------------------------------------
# Fluorescence line cross-sections — success + error
# ---------------------------------------------------------------------------


class TestCSFluorLine:
    def test_fe_ka_20kev(self):
        data = _parse(CS_FluorLine(26, "KA_LINE", 20.0))
        _assert_success(data, "CS_FluorLine")
        assert data["result"] > 0

    def test_below_edge(self):
        data = _parse(CS_FluorLine(26, "KA_LINE", 5.0))
        _assert_error(data, "CS_FluorLine")


class TestCSbFluorLine:
    def test_fe_ka_20kev(self):
        data = _parse(CSb_FluorLine(26, "KA_LINE", 20.0))
        _assert_success(data, "CSb_FluorLine")
        assert data["units"] == "barn/atom"
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CSb_FluorLine(26, "FAKE", 20.0))
        _assert_error(data, "CSb_FluorLine")


class TestCSFluorShell:
    def test_fe_k_20kev(self):
        data = _parse(CS_FluorShell(26, "K_SHELL", 20.0))
        _assert_success(data, "CS_FluorShell")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_FluorShell(26, "FAKE", 20.0))
        _assert_error(data, "CS_FluorShell")


class TestCSbFluorShell:
    def test_fe_k_20kev(self):
        data = _parse(CSb_FluorShell(26, "K_SHELL", 20.0))
        _assert_success(data, "CSb_FluorShell")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CSb_FluorShell(26, "FAKE", 20.0))
        _assert_error(data, "CSb_FluorShell")


# ---------------------------------------------------------------------------
# Kissel fluorescence LINE cross-sections — parametrized success + error
# ---------------------------------------------------------------------------


_KISSEL_LINE_FUNCS = [
    CS_FluorLine_Kissel,
    CSb_FluorLine_Kissel,
    CS_FluorLine_Kissel_Cascade,
    CSb_FluorLine_Kissel_Cascade,
    CS_FluorLine_Kissel_Nonradiative_Cascade,
    CSb_FluorLine_Kissel_Nonradiative_Cascade,
    CS_FluorLine_Kissel_Radiative_Cascade,
    CSb_FluorLine_Kissel_Radiative_Cascade,
    CS_FluorLine_Kissel_no_Cascade,
    CSb_FluorLine_Kissel_no_Cascade,
]


@pytest.mark.parametrize("func", _KISSEL_LINE_FUNCS, ids=lambda f: f.__name__)
class TestKisselLineFunctions:
    def test_success(self, func):
        data = _parse(func(26, "KA_LINE", 20.0))
        _assert_success(data, func.__name__)
        assert data["result"] > 0

    def test_error(self, func):
        data = _parse(func(26, "FAKE", 20.0))
        _assert_error(data, func.__name__)


# ---------------------------------------------------------------------------
# Kissel fluorescence SHELL cross-sections — parametrized success + error
# ---------------------------------------------------------------------------


_KISSEL_SHELL_FUNCS = [
    CS_FluorShell_Kissel,
    CSb_FluorShell_Kissel,
    CS_FluorShell_Kissel_Cascade,
    CSb_FluorShell_Kissel_Cascade,
    CS_FluorShell_Kissel_Nonradiative_Cascade,
    CSb_FluorShell_Kissel_Nonradiative_Cascade,
    CS_FluorShell_Kissel_Radiative_Cascade,
    CSb_FluorShell_Kissel_Radiative_Cascade,
    CS_FluorShell_Kissel_no_Cascade,
    CSb_FluorShell_Kissel_no_Cascade,
]


@pytest.mark.parametrize("func", _KISSEL_SHELL_FUNCS, ids=lambda f: f.__name__)
class TestKisselShellFunctions:
    def test_success(self, func):
        data = _parse(func(26, "K_SHELL", 20.0))
        _assert_success(data, func.__name__)
        assert data["result"] > 0

    def test_error(self, func):
        data = _parse(func(26, "FAKE", 20.0))
        _assert_error(data, func.__name__)


# ---------------------------------------------------------------------------
# Kissel total/photo cross-sections
# ---------------------------------------------------------------------------


class TestCSTotalKissel:
    def test_fe_10kev(self):
        data = _parse(CS_Total_Kissel(26, 10.0))
        _assert_success(data, "CS_Total_Kissel")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_Total_Kissel(0, 10.0))
        _assert_error(data, "CS_Total_Kissel")


class TestCSbTotalKissel:
    def test_fe_10kev(self):
        data = _parse(CSb_Total_Kissel(26, 10.0))
        _assert_success(data, "CSb_Total_Kissel")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CSb_Total_Kissel(0, 10.0))
        _assert_error(data, "CSb_Total_Kissel")


class TestCSPhotoTotal:
    def test_fe_10kev(self):
        data = _parse(CS_Photo_Total(26, 10.0))
        _assert_success(data, "CS_Photo_Total")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_Photo_Total(0, 10.0))
        _assert_error(data, "CS_Photo_Total")


class TestCSbPhotoTotal:
    def test_fe_10kev(self):
        data = _parse(CSb_Photo_Total(26, 10.0))
        _assert_success(data, "CSb_Photo_Total")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CSb_Photo_Total(0, 10.0))
        _assert_error(data, "CSb_Photo_Total")


class TestCSPhotoPartial:
    def test_fe_k_20kev(self):
        data = _parse(CS_Photo_Partial(26, "K_SHELL", 20.0))
        _assert_success(data, "CS_Photo_Partial")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_Photo_Partial(26, "FAKE", 20.0))
        _assert_error(data, "CS_Photo_Partial")


class TestCSbPhotoPartial:
    def test_fe_k_20kev(self):
        data = _parse(CSb_Photo_Partial(26, "K_SHELL", 20.0))
        _assert_success(data, "CSb_Photo_Partial")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CSb_Photo_Partial(26, "FAKE", 20.0))
        _assert_error(data, "CSb_Photo_Partial")


# ---------------------------------------------------------------------------
# Differential cross-sections — success + error
# ---------------------------------------------------------------------------


class TestDCSRayl:
    def test_fe_10kev(self):
        data = _parse(DCS_Rayl(26, 10.0, math.pi / 4))
        _assert_success(data, "DCS_Rayl")
        assert data["units"] == "cm2/g/sr"
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(DCS_Rayl(0, 10.0, math.pi / 4))
        _assert_error(data, "DCS_Rayl")


class TestDCSCompt:
    def test_fe_10kev(self):
        data = _parse(DCS_Compt(26, 10.0, math.pi / 4))
        _assert_success(data, "DCS_Compt")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(DCS_Compt(0, 10.0, math.pi / 4))
        _assert_error(data, "DCS_Compt")


class TestDCSbRayl:
    def test_fe_10kev(self):
        data = _parse(DCSb_Rayl(26, 10.0, math.pi / 4))
        _assert_success(data, "DCSb_Rayl")
        assert data["units"] == "barn/atom/sr"
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(DCSb_Rayl(0, 10.0, math.pi / 4))
        _assert_error(data, "DCSb_Rayl")


class TestDCSbCompt:
    def test_fe_10kev(self):
        data = _parse(DCSb_Compt(26, 10.0, math.pi / 4))
        _assert_success(data, "DCSb_Compt")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(DCSb_Compt(0, 10.0, math.pi / 4))
        _assert_error(data, "DCSb_Compt")


class TestDCSPRayl:
    def test_fe_10kev(self):
        data = _parse(DCSP_Rayl(26, 10.0, math.pi / 4, 0.0))
        _assert_success(data, "DCSP_Rayl")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(DCSP_Rayl(0, 10.0, math.pi / 4, 0.0))
        _assert_error(data, "DCSP_Rayl")


class TestDCSPCompt:
    def test_fe_10kev(self):
        data = _parse(DCSP_Compt(26, 10.0, math.pi / 4, 0.0))
        _assert_success(data, "DCSP_Compt")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(DCSP_Compt(0, 10.0, math.pi / 4, 0.0))
        _assert_error(data, "DCSP_Compt")


class TestDCSPbRayl:
    def test_fe_10kev(self):
        data = _parse(DCSPb_Rayl(26, 10.0, math.pi / 4, 0.0))
        _assert_success(data, "DCSPb_Rayl")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(DCSPb_Rayl(0, 10.0, math.pi / 4, 0.0))
        _assert_error(data, "DCSPb_Rayl")


class TestDCSPbCompt:
    def test_fe_10kev(self):
        data = _parse(DCSPb_Compt(26, 10.0, math.pi / 4, 0.0))
        _assert_success(data, "DCSPb_Compt")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(DCSPb_Compt(0, 10.0, math.pi / 4, 0.0))
        _assert_error(data, "DCSPb_Compt")


# ---------------------------------------------------------------------------
# Scattering factors — success + error
# ---------------------------------------------------------------------------


class TestFFRayl:
    def test_fe(self):
        data = _parse(FF_Rayl(26, 0.5))
        _assert_success(data, "FF_Rayl")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(FF_Rayl(0, 0.5))
        _assert_error(data, "FF_Rayl")


class TestSFCompt:
    def test_fe(self):
        data = _parse(SF_Compt(26, 0.5))
        _assert_success(data, "SF_Compt")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(SF_Compt(0, 0.5))
        _assert_error(data, "SF_Compt")


class TestMomentTransf:
    def test_basic(self):
        data = _parse(MomentTransf(10.0, math.pi / 4))
        _assert_success(data, "MomentTransf")
        assert data["units"] == "1/Angstrom"
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(MomentTransf(0.0, math.pi / 4))
        _assert_error(data, "MomentTransf")


class TestComptonEnergy:
    def test_basic(self):
        data = _parse(ComptonEnergy(100.0, math.pi / 2))
        _assert_success(data, "ComptonEnergy")
        assert data["units"] == "keV"
        assert 0 < data["result"] < 100.0

    def test_invalid(self):
        data = _parse(ComptonEnergy(0.0, math.pi / 2))
        _assert_error(data, "ComptonEnergy")


class TestFi:
    def test_fe(self):
        data = _parse(Fi(26, 10.0))
        _assert_success(data, "Fi")
        assert isinstance(data["result"], float)

    def test_invalid(self):
        data = _parse(Fi(0, 10.0))
        _assert_error(data, "Fi")


class TestFii:
    def test_fe(self):
        data = _parse(Fii(26, 10.0))
        _assert_success(data, "Fii")
        assert isinstance(data["result"], float)

    def test_invalid(self):
        data = _parse(Fii(0, 10.0))
        _assert_error(data, "Fii")


class TestComptonProfile:
    def test_fe(self):
        data = _parse(ComptonProfile(26, 0.0))
        _assert_success(data, "ComptonProfile")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(ComptonProfile(0, 0.0))
        _assert_error(data, "ComptonProfile")


class TestComptonProfilePartial:
    def test_fe_k(self):
        data = _parse(ComptonProfile_Partial(26, "K_SHELL", 0.0))
        _assert_success(data, "ComptonProfile_Partial")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(ComptonProfile_Partial(26, "FAKE", 0.0))
        _assert_error(data, "ComptonProfile_Partial")


# ---------------------------------------------------------------------------
# Auger and Coster-Kronig — success + error
# ---------------------------------------------------------------------------


class TestAugerRate:
    def test_fe(self):
        data = _parse(AugerRate(26, "K_L1L1_AUGER"))
        _assert_success(data, "AugerRate")
        assert data["result"] >= 0

    def test_invalid(self):
        data = _parse(AugerRate(26, "FAKE"))
        _assert_error(data, "AugerRate")


class TestAugerYield:
    def test_fe_k(self):
        data = _parse(AugerYield(26, "K_SHELL"))
        _assert_success(data, "AugerYield")
        assert 0 < data["result"] < 1

    def test_invalid(self):
        data = _parse(AugerYield(26, "FAKE"))
        _assert_error(data, "AugerYield")


class TestCosKronTransProb:
    def test_fe(self):
        data = _parse(CosKronTransProb(26, "FL13_TRANS"))
        _assert_success(data, "CosKronTransProb")
        assert data["result"] >= 0

    def test_invalid(self):
        data = _parse(CosKronTransProb(26, "FAKE"))
        _assert_error(data, "CosKronTransProb")


# ---------------------------------------------------------------------------
# Compound cross-sections (cm2/g) — success + error
# ---------------------------------------------------------------------------


class TestCSTotalCP:
    def test_sio2_10kev(self):
        data = _parse(CS_Total_CP("SiO2", 10.0))
        _assert_success(data, "CS_Total_CP")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_Total_CP("", 10.0))
        _assert_error(data, "CS_Total_CP")


class TestCSPhotoCP:
    def test_h2o_10kev(self):
        data = _parse(CS_Photo_CP("H2O", 10.0))
        _assert_success(data, "CS_Photo_CP")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_Photo_CP("", 10.0))
        _assert_error(data, "CS_Photo_CP")


class TestCSRaylCP:
    def test_h2o_10kev(self):
        data = _parse(CS_Rayl_CP("H2O", 10.0))
        _assert_success(data, "CS_Rayl_CP")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_Rayl_CP("", 10.0))
        _assert_error(data, "CS_Rayl_CP")


class TestCSComptCP:
    def test_h2o_10kev(self):
        data = _parse(CS_Compt_CP("H2O", 10.0))
        _assert_success(data, "CS_Compt_CP")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_Compt_CP("", 10.0))
        _assert_error(data, "CS_Compt_CP")


class TestCSEnergyCP:
    def test_h2o_10kev(self):
        data = _parse(CS_Energy_CP("H2O", 10.0))
        _assert_success(data, "CS_Energy_CP")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_Energy_CP("", 10.0))
        _assert_error(data, "CS_Energy_CP")


class TestCSTotalKisselCP:
    def test_sio2_10kev(self):
        data = _parse(CS_Total_Kissel_CP("SiO2", 10.0))
        _assert_success(data, "CS_Total_Kissel_CP")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_Total_Kissel_CP("", 10.0))
        _assert_error(data, "CS_Total_Kissel_CP")


class TestCSPhotoTotalCP:
    def test_sio2_10kev(self):
        data = _parse(CS_Photo_Total_CP("SiO2", 10.0))
        _assert_success(data, "CS_Photo_Total_CP")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CS_Photo_Total_CP("", 10.0))
        _assert_error(data, "CS_Photo_Total_CP")


# ---------------------------------------------------------------------------
# Compound cross-sections (barn/atom) — success + error
# ---------------------------------------------------------------------------


class TestCSbTotalCP:
    def test_sio2_10kev(self):
        data = _parse(CSb_Total_CP("SiO2", 10.0))
        _assert_success(data, "CSb_Total_CP")
        assert data["units"] == "barn/atom"
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CSb_Total_CP("", 10.0))
        _assert_error(data, "CSb_Total_CP")


class TestCSbPhotoCP:
    def test_h2o_10kev(self):
        data = _parse(CSb_Photo_CP("H2O", 10.0))
        _assert_success(data, "CSb_Photo_CP")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CSb_Photo_CP("", 10.0))
        _assert_error(data, "CSb_Photo_CP")


class TestCSbRaylCP:
    def test_h2o_10kev(self):
        data = _parse(CSb_Rayl_CP("H2O", 10.0))
        _assert_success(data, "CSb_Rayl_CP")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CSb_Rayl_CP("", 10.0))
        _assert_error(data, "CSb_Rayl_CP")


class TestCSbComptCP:
    def test_h2o_10kev(self):
        data = _parse(CSb_Compt_CP("H2O", 10.0))
        _assert_success(data, "CSb_Compt_CP")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CSb_Compt_CP("", 10.0))
        _assert_error(data, "CSb_Compt_CP")


class TestCSbTotalKisselCP:
    def test_sio2_10kev(self):
        data = _parse(CSb_Total_Kissel_CP("SiO2", 10.0))
        _assert_success(data, "CSb_Total_Kissel_CP")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CSb_Total_Kissel_CP("", 10.0))
        _assert_error(data, "CSb_Total_Kissel_CP")


class TestCSbPhotoTotalCP:
    def test_sio2_10kev(self):
        data = _parse(CSb_Photo_Total_CP("SiO2", 10.0))
        _assert_success(data, "CSb_Photo_Total_CP")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(CSb_Photo_Total_CP("", 10.0))
        _assert_error(data, "CSb_Photo_Total_CP")


# ---------------------------------------------------------------------------
# Compound differential cross-sections — success + error
# ---------------------------------------------------------------------------


_DCS_CP_3_FUNCS = [
    DCS_Rayl_CP,
    DCS_Compt_CP,
    DCSb_Rayl_CP,
    DCSb_Compt_CP,
]


@pytest.mark.parametrize("func", _DCS_CP_3_FUNCS, ids=lambda f: f.__name__)
class TestDCSCPFunctions:
    def test_success(self, func):
        data = _parse(func("H2O", 10.0, math.pi / 4))
        _assert_success(data, func.__name__)
        assert data["result"] > 0

    def test_error(self, func):
        data = _parse(func("", 10.0, math.pi / 4))
        _assert_error(data, func.__name__)


_DCSP_CP_4_FUNCS = [
    DCSP_Rayl_CP,
    DCSP_Compt_CP,
    DCSPb_Rayl_CP,
    DCSPb_Compt_CP,
]


@pytest.mark.parametrize("func", _DCSP_CP_4_FUNCS, ids=lambda f: f.__name__)
class TestDCSPCPFunctions:
    def test_success(self, func):
        data = _parse(func("H2O", 10.0, math.pi / 4, 0.0))
        _assert_success(data, func.__name__)
        assert data["result"] > 0

    def test_error(self, func):
        data = _parse(func("", 10.0, math.pi / 4, 0.0))
        _assert_error(data, func.__name__)


# ---------------------------------------------------------------------------
# Refractive index — success + error
# ---------------------------------------------------------------------------


class TestRefractiveIndexRe:
    def test_sio2(self):
        data = _parse(Refractive_Index_Re("SiO2", 10.0, 2.65))
        _assert_success(data, "Refractive_Index_Re")
        assert 0.9 < data["result"] <= 1.0

    def test_invalid(self):
        data = _parse(Refractive_Index_Re("", 10.0, 2.65))
        _assert_error(data, "Refractive_Index_Re")


class TestRefractiveIndexIm:
    def test_sio2(self):
        data = _parse(Refractive_Index_Im("SiO2", 10.0, 2.65))
        _assert_success(data, "Refractive_Index_Im")
        assert data["result"] > 0

    def test_invalid(self):
        data = _parse(Refractive_Index_Im("", 10.0, 2.65))
        _assert_error(data, "Refractive_Index_Im")


# ---------------------------------------------------------------------------
# NIST compounds — success + error
# ---------------------------------------------------------------------------


class TestGetCompoundDataNISTByName:
    def test_water(self):
        data = _parse(GetCompoundDataNISTByName("Water, Liquid"))
        _assert_success(data, "GetCompoundDataNISTByName")
        assert data["result"]["name"] == "Water, Liquid"
        assert data["result"]["nElements"] == 2
        assert data["result"]["density"] > 0

    def test_invalid_name(self):
        data = _parse(GetCompoundDataNISTByName("Not A Real Compound"))
        _assert_error(data, "GetCompoundDataNISTByName")


class TestGetCompoundDataNISTByIndex:
    def test_index_zero(self):
        data = _parse(GetCompoundDataNISTByIndex(0))
        _assert_success(data, "GetCompoundDataNISTByIndex")
        assert "name" in data["result"]
        assert data["result"]["nElements"] > 0

    def test_invalid_index(self):
        data = _parse(GetCompoundDataNISTByIndex(9999))
        _assert_error(data, "GetCompoundDataNISTByIndex")


class TestGetCompoundDataNISTList:
    def test_returns_list(self):
        data = _parse(GetCompoundDataNISTList())
        _assert_success(data, "GetCompoundDataNISTList")
        assert isinstance(data["result"], list)
        assert len(data["result"]) > 0

    def test_error(self):
        with patch("xraylib_mcp_server.server.xraylib.GetCompoundDataNISTList",
                    side_effect=RuntimeError("boom")):
            data = _parse(GetCompoundDataNISTList())
            _assert_error(data, "GetCompoundDataNISTList")


# ---------------------------------------------------------------------------
# Constant listing tools — success + error
# ---------------------------------------------------------------------------


class TestListConstants:
    def test_list_line_constants(self):
        data = _parse(ListLineConstants())
        _assert_success(data, "ListLineConstants")
        assert "KL3_LINE" in data["result"]

    def test_list_shell_constants(self):
        data = _parse(ListShellConstants())
        _assert_success(data, "ListShellConstants")
        assert "K_SHELL" in data["result"]

    def test_list_transition_constants(self):
        data = _parse(ListTransitionConstants())
        _assert_success(data, "ListTransitionConstants")
        assert len(data["result"]) > 0

    def test_list_auger_constants(self):
        data = _parse(ListAugerConstants())
        _assert_success(data, "ListAugerConstants")
        assert len(data["result"]) > 0

    def test_list_nist_compound_constants(self):
        data = _parse(ListNISTCompoundConstants())
        _assert_success(data, "ListNISTCompoundConstants")
        assert len(data["result"]) > 0


class TestListConstantsErrors:
    def test_list_line_error(self):
        with patch("xraylib_mcp_server.server.list_lines",
                    side_effect=RuntimeError("boom")):
            data = _parse(ListLineConstants())
            _assert_error(data, "ListLineConstants")

    def test_list_shell_error(self):
        with patch("xraylib_mcp_server.server.list_shells",
                    side_effect=RuntimeError("boom")):
            data = _parse(ListShellConstants())
            _assert_error(data, "ListShellConstants")

    def test_list_transition_error(self):
        with patch("xraylib_mcp_server.server.list_transitions",
                    side_effect=RuntimeError("boom")):
            data = _parse(ListTransitionConstants())
            _assert_error(data, "ListTransitionConstants")

    def test_list_auger_error(self):
        with patch("xraylib_mcp_server.server.list_auger_transitions",
                    side_effect=RuntimeError("boom")):
            data = _parse(ListAugerConstants())
            _assert_error(data, "ListAugerConstants")

    def test_list_nist_error(self):
        with patch("xraylib_mcp_server.server.list_nist_compounds",
                    side_effect=RuntimeError("boom")):
            data = _parse(ListNISTCompoundConstants())
            _assert_error(data, "ListNISTCompoundConstants")
