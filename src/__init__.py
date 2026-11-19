"""First-Principles Exergy and Economic Audit for Terrestrial Helium-3 Extraction."""

from .he3_exergy_engine import (
    audit_accelerator_and_plasma_synthesis,
    audit_hybrid_cryo_cascade,
    audit_quantum_cryo_supply,
    audit_reactor_tritium_decay,
    generate_exergy_figure,
    run_full_he3_audit,
)

__all__ = [
    "audit_accelerator_and_plasma_synthesis",
    "audit_hybrid_cryo_cascade",
    "audit_quantum_cryo_supply",
    "audit_reactor_tritium_decay",
    "generate_exergy_figure",
    "run_full_he3_audit",
]
