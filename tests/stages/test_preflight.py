"""The preflight gate, against fabricated probe results.

Every blocking rule must fire on its known case and stay silent on a healthy
machine; the macOS probes themselves (``sysctl``, ``vm_stat``, ``ps``, the
Ollama HTTP calls) are replaced, not exercised.
"""

import pytest

from factory.infra import preflight

HEALTHY = {
    "_disk_free_gb": lambda *a, **k: 120.0,
    "_swap_gb": lambda: {"total": 0.0, "used": 0.0, "free": 0.0},
    "_swap_froid": lambda *a, **k: False,
    "_pressure_level": lambda: 1,
    "_busy_daemons": lambda: [],
    "_probe_generation": lambda *a, **k: None,
    "_loaded_llms": lambda: [],
}


@pytest.fixture
def healthy(monkeypatch):
    for name, fn in HEALTHY.items():
        monkeypatch.setattr(preflight, name, fn)
    return monkeypatch


def test_healthy_machine_passes_without_warnings(healthy):
    assert preflight.preflight() == []
    assert preflight.preflight(chrono=True) == []


def test_low_disk_blocks(healthy):
    healthy.setattr(preflight, "_disk_free_gb", lambda *a, **k: 5.0)
    with pytest.raises(preflight.PreflightError, match="Disque"):
        preflight.preflight()


def test_low_swap_blocks_only_when_timing_and_only_if_hot(healthy):
    healthy.setattr(preflight, "_swap_gb", lambda: {"total": 4.0, "used": 3.6, "free": 0.4})
    warns = preflight.preflight()                       # not timing: warning only
    assert len(warns) == 1 and "Swap" in warns[0] and "DÉCHARGER" in warns[0]
    with pytest.raises(preflight.PreflightError, match="ininterprétables"):
        preflight.preflight(chrono=True)
    healthy.setattr(preflight, "_swap_froid", lambda *a, **k: True)
    warns = preflight.preflight(chrono=True)            # cold swap: interpretable
    assert len(warns) == 1 and "FROID" in warns[0]


def test_memory_pressure_levels(healthy):
    healthy.setattr(preflight, "_pressure_level", lambda: 2)
    assert any("élevée" in w for w in preflight.preflight())
    healthy.setattr(preflight, "_pressure_level", lambda: 4)
    with pytest.raises(preflight.PreflightError, match="CRITIQUE"):
        preflight.preflight()
    healthy.setattr(preflight, "_pressure_level", lambda: None)
    assert any("illisible" in w for w in preflight.preflight())


def test_maintenance_daemons_warn_then_block(healthy):
    healthy.setattr(preflight, "_busy_daemons", lambda: [("mediaanalysisd", 45.0)])
    assert any("Surveiller" in w for w in preflight.preflight())
    healthy.setattr(preflight, "_busy_daemons", lambda: [("mediaanalysisd", 197.0)])
    with pytest.raises(preflight.PreflightError, match="mediaanalysisd 197"):
        preflight.preflight()


def test_ollama_that_cannot_generate_blocks(healthy):
    healthy.setattr(preflight, "_probe_generation",
                    lambda *a, **k: "HTTP 500 sur /api/generate (qwen)")
    with pytest.raises(preflight.PreflightError, match="kickstart"):
        preflight.preflight()


def test_two_hot_llms_block_one_is_fine(healthy):
    healthy.setattr(preflight, "_loaded_llms",
                    lambda: [{"name": "nemo", "size": 13e9}])
    assert preflight.preflight() == []
    healthy.setattr(preflight, "_loaded_llms",
                    lambda: [{"name": "nemo", "size": 13e9}, {"name": "qwen", "size": 4.8e9}])
    with pytest.raises(preflight.PreflightError, match="Co-résidence"):
        preflight.preflight()
    healthy.setattr(preflight, "_loaded_llms", lambda: None)
    assert any("injoignable" in w for w in preflight.preflight())


def test_non_strict_mode_returns_blocking_conditions_as_text(healthy):
    healthy.setattr(preflight, "_disk_free_gb", lambda *a, **k: 5.0)
    out = preflight.preflight(strict=False)
    assert len(out) == 1 and "Disque" in out[0]


def test_report_reads_the_same_probes(healthy):
    txt = preflight.report()
    assert "aucun swapfile" in txt and "LLM chauds : aucun" in txt
