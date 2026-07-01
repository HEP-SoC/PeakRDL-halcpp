"""Golden-file integration tests for HalExporter.

Run pytest --update-golden to regenerate expected/ after intentional template changes.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from peakrdl_halcpp import HalExporter

RDL_DIR = Path(__file__).parent / "rdl"
EXPECTED_DIR = Path(__file__).parent / "expected"

# (case_name, rdl_filename, export kwargs)
CASES = [
    ("atxmega_spi", "atxmega_spi.rdl", {}),
    ("regs_and_mem", "regs_and_mem.rdl", {}),
    ("bus_flatten", "bus_flatten.rdl", {}),
    ("bus_flatten_skip", "bus_flatten.rdl", {"skip_buses": True}),
    ("enum_field", "enum_field.rdl", {}),
    ("array_reg", "array_reg.rdl", {}),
]


@pytest.mark.parametrize("case_name,rdl_file,export_kwargs", CASES)
def test_golden_output(case_name, rdl_file, export_kwargs, update_golden, compile_rdl, tmp_path):
    top = compile_rdl(RDL_DIR / rdl_file)
    exporter = HalExporter()
    exporter.export(node=top, outdir=str(tmp_path), **export_kwargs)

    # Only compare generated .h files at the root (not the copied include/ headers)
    generated = {f for f in tmp_path.iterdir() if f.suffix == ".h"}
    expected_dir = EXPECTED_DIR / case_name

    if update_golden:
        expected_dir.mkdir(parents=True, exist_ok=True)
        for gen_file in generated:
            (expected_dir / gen_file.name).write_text(gen_file.read_text())
        pytest.skip(f"Golden files updated in {expected_dir}")

    assert expected_dir.exists(), f"No golden directory for '{case_name}'. Run: pytest --update-golden"

    expected_names = {f.name for f in expected_dir.iterdir() if f.suffix == ".h"}
    generated_names = {f.name for f in generated}
    assert generated_names == expected_names, (
        f"[{case_name}] file set mismatch — expected {expected_names}, got {generated_names}"
    )

    for gen_file in sorted(generated):
        expected_text = (expected_dir / gen_file.name).read_text()
        assert gen_file.read_text() == expected_text, f"[{case_name}] content mismatch in {gen_file.name}"
