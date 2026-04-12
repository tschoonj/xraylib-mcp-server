"""Tests for xraylib_mcp.constants module."""

import pytest
import xraylib

from xraylib_mcp_server.constants import (
    list_auger_transitions,
    list_lines,
    list_nist_compounds,
    list_shells,
    list_transitions,
    resolve_auger,
    resolve_line,
    resolve_nist_compound,
    resolve_shell,
    resolve_transition,
)


# ---------------------------------------------------------------------------
# resolve_line
# ---------------------------------------------------------------------------


class TestResolveLine:
    def test_full_name(self):
        assert resolve_line("KL3_LINE") == xraylib.KL3_LINE

    def test_without_suffix(self):
        assert resolve_line("KL3") == xraylib.KL3_LINE

    def test_case_insensitive(self):
        assert resolve_line("kl3_line") == xraylib.KL3_LINE

    def test_whitespace_stripped(self):
        assert resolve_line("  KL3_LINE  ") == xraylib.KL3_LINE

    def test_ka_line(self):
        assert resolve_line("KA_LINE") == xraylib.KA_LINE

    def test_la1_line(self):
        assert resolve_line("LA1_LINE") == xraylib.LA1_LINE

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown line constant"):
            resolve_line("FAKE_LINE")

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="Unknown line constant"):
            resolve_line("")


# ---------------------------------------------------------------------------
# resolve_shell
# ---------------------------------------------------------------------------


class TestResolveShell:
    def test_full_name(self):
        assert resolve_shell("K_SHELL") == xraylib.K_SHELL

    def test_without_suffix(self):
        assert resolve_shell("K") == xraylib.K_SHELL

    def test_l1_shell(self):
        assert resolve_shell("L1_SHELL") == xraylib.L1_SHELL

    def test_m5_shell(self):
        assert resolve_shell("M5_SHELL") == xraylib.M5_SHELL

    def test_case_insensitive(self):
        assert resolve_shell("k_shell") == xraylib.K_SHELL

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown shell constant"):
            resolve_shell("FAKE_SHELL")


# ---------------------------------------------------------------------------
# resolve_transition
# ---------------------------------------------------------------------------


class TestResolveTransition:
    def test_full_name(self):
        assert resolve_transition("FL13_TRANS") == xraylib.FL13_TRANS

    def test_without_suffix(self):
        assert resolve_transition("FL13") == xraylib.FL13_TRANS

    def test_case_insensitive(self):
        assert resolve_transition("fl13_trans") == xraylib.FL13_TRANS

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown transition constant"):
            resolve_transition("FAKE_TRANS")


# ---------------------------------------------------------------------------
# resolve_auger
# ---------------------------------------------------------------------------


class TestResolveAuger:
    def test_full_name(self):
        assert resolve_auger("K_L1L1_AUGER") == xraylib.K_L1L1_AUGER

    def test_without_suffix(self):
        assert resolve_auger("K_L1L1") == xraylib.K_L1L1_AUGER

    def test_case_insensitive(self):
        assert resolve_auger("k_l1l1_auger") == xraylib.K_L1L1_AUGER

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown Auger constant"):
            resolve_auger("FAKE_AUGER")


# ---------------------------------------------------------------------------
# resolve_nist_compound
# ---------------------------------------------------------------------------


class TestResolveNistCompound:
    def test_full_name(self):
        val = resolve_nist_compound("NIST_COMPOUND_WATER_LIQUID")
        assert isinstance(val, int)

    def test_without_prefix(self):
        val = resolve_nist_compound("WATER_LIQUID")
        assert val == resolve_nist_compound("NIST_COMPOUND_WATER_LIQUID")

    def test_case_insensitive(self):
        val = resolve_nist_compound("nist_compound_water_liquid")
        assert isinstance(val, int)

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown NIST compound constant"):
            resolve_nist_compound("FAKE_COMPOUND")


# ---------------------------------------------------------------------------
# list_* functions
# ---------------------------------------------------------------------------


class TestListFunctions:
    def test_list_lines_nonempty(self):
        lines = list_lines()
        assert len(lines) > 0
        assert all(name.endswith("_LINE") for name in lines)

    def test_list_lines_sorted(self):
        lines = list_lines()
        assert lines == sorted(lines)

    def test_list_lines_contains_known(self):
        lines = list_lines()
        assert "KL3_LINE" in lines
        assert "KA_LINE" in lines

    def test_list_shells_nonempty(self):
        shells = list_shells()
        assert len(shells) > 0
        assert all(name.endswith("_SHELL") for name in shells)

    def test_list_shells_contains_known(self):
        shells = list_shells()
        assert "K_SHELL" in shells
        assert "L1_SHELL" in shells

    def test_list_transitions_nonempty(self):
        trans = list_transitions()
        assert len(trans) > 0
        assert all(name.endswith("_TRANS") for name in trans)

    def test_list_auger_transitions_nonempty(self):
        auger = list_auger_transitions()
        assert len(auger) > 0
        assert all(name.endswith("_AUGER") for name in auger)

    def test_list_nist_compounds_nonempty(self):
        nist = list_nist_compounds()
        assert len(nist) > 0
        assert all(name.startswith("NIST_COMPOUND_") for name in nist)
