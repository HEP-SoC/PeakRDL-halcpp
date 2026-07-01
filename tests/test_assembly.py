"""Assembly quality tests: verify generated C++ compiles to zero-cost abstractions.

Every register and field access must inline down to raw load/store instructions
with no function-call overhead. Tests parametrize over available compilers;
cross-compilers (RISC-V) are silently skipped when not installed.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from peakrdl_halcpp import HalExporter

RDL_DIR = Path(__file__).parent / "rdl"

# ---------------------------------------------------------------------------
# C++ driver exercising the HAL at the assembly level.
# extern "C" prevents name mangling so function labels are easy to locate.
# The raw_* functions serve as baselines: a correct HAL must emit the same
# number of instructions as a direct volatile pointer access.
# ---------------------------------------------------------------------------
_DRIVER_CPP = """\
#include "atxmega_spi_hal.h"
#include <cstdint>

using SPI = ATXMEGA_SPI_HAL<0x40000000>;

// Register read — expect a single 32-bit load.
// uint8_t matches the HAL's dataType for WIDTH=8; both functions return via %al.
extern "C" uint8_t hal_ctrl_get()          { return SPI::CTRL.get(); }
extern "C" uint8_t raw_ctrl_get()          { return *(volatile uint32_t *)0x40000000U; }

// Register write — expect a single 32-bit store.
// uint8_t matches RegWrMixin::set() dataType; both functions zero-extend before storing.
extern "C" void    hal_ctrl_set(uint8_t v) { SPI::CTRL.set(v); }
extern "C" void    raw_ctrl_set(uint8_t v) { *(volatile uint32_t *)0x40000000U = v; }

// Field read — expect load + mask + shift (no subroutine calls)
extern "C" uint8_t hal_prescaler_get()          { return SPI::CTRL.PRESCALER.get(); }

// Field write — expect read-modify-write (no subroutine calls)
extern "C" void    hal_prescaler_set(uint8_t v) { SPI::CTRL.PRESCALER.set(v); }
"""

# ---------------------------------------------------------------------------
# Compilers
# ---------------------------------------------------------------------------
# (executable, test_id, flags)
# -Wno-int-to-pointer-cast: the HAL uses uint32_t for addresses (designed for 32-bit targets);
# on a 64-bit host this triggers a harmless warning in arch_io.h.
# riscv64-unknown-elf-g++ targets both RV32 and RV64 via -march/-mabi flags.
# On Ubuntu: sudo apt-get install gcc-riscv64-unknown-elf
_COMPILERS: list[tuple[str, str, list[str]]] = [
    ("g++", "g++", ["-std=c++17", "-O2", "-S", "-Wno-int-to-pointer-cast"]),
    ("clang++", "clang++", ["-std=c++17", "-O2", "-S", "-Wno-int-to-pointer-cast"]),
    ("riscv64-unknown-elf-g++", "rv32", ["-std=c++17", "-O2", "-S", "-march=rv32i", "-mabi=ilp32"]),
    ("riscv64-unknown-elf-g++", "rv64", ["-std=c++17", "-O2", "-S", "-march=rv64im", "-mabi=lp64"]),
]

# Subroutine-call mnemonics for x86 / ARM / AArch64
_CALL_MNEMONICS = frozenset({"call", "bl", "blx", "blr"})


def _compiler_params() -> list:
    return [
        pytest.param(
            compiler,
            flags,
            id=test_id,
            marks=pytest.mark.skipif(not shutil.which(compiler), reason=f"{compiler} not found in PATH"),
        )
        for compiler, test_id, flags in _COMPILERS
    ]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _compile_to_asm(compiler: str, flags: list[str], src_dir: Path) -> str:
    """Compile test_driver.cpp to assembly and return the file contents."""
    safe = re.sub(r"[^a-zA-Z0-9]", "_", compiler)
    asm_file = src_dir / f"driver_{safe}.s"
    result = subprocess.run(
        [compiler, *flags, f"-I{src_dir}", str(src_dir / "test_driver.cpp"), "-o", str(asm_file)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"{compiler} compilation failed:\n{result.stderr}"
    return asm_file.read_text()


# Matches public function labels (no leading dot) — stops function-body extraction.
# Dot-prefixed labels like .LFBxxx (GCC debug frames) are intentionally excluded
# so they don't prematurely terminate parsing.
_LABEL_RE = re.compile(r"^[a-zA-Z_$][a-zA-Z0-9_$\.@]*:")


def _function_body(asm: str, func_name: str) -> list[str]:
    """Return non-directive instruction lines for *func_name*.

    Handles both Linux ELF (func_name:) and macOS Mach-O (_func_name:) conventions.
    """
    targets = {f"{func_name}:", f"_{func_name}:"}
    instructions: list[str] = []
    in_func = False

    for line in asm.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "//")):
            continue
        if stripped in targets:
            in_func = True
            continue
        if in_func:
            if _LABEL_RE.match(stripped):
                break
            if not stripped.startswith("."):
                instructions.append(stripped)

    return instructions


def _has_call(instructions: list[str]) -> bool:
    """Return True if any instruction is a subroutine call on any supported ISA."""
    for instr in instructions:
        mnemonic = instr.split()[0].lower().rstrip(",")
        if mnemonic in _CALL_MNEMONICS:
            return True
        # RISC-V: jal/jalr with ra (x1) as destination = call.
        # jal x0 / jalr x0 are plain jump / return — not calls.
        if mnemonic in ("jal", "jalr"):
            parts = instr.split()
            if len(parts) >= 2 and parts[1].rstrip(",").lower() in ("ra", "x1"):
                return True
    return False


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def spi_hal_dir(compile_rdl, tmp_path):
    """Export atxmega_spi HAL into a temp directory and place the driver there."""
    top = compile_rdl(RDL_DIR / "atxmega_spi.rdl")
    HalExporter().export(node=top, outdir=str(tmp_path))
    (tmp_path / "test_driver.cpp").write_text(_DRIVER_CPP)
    return tmp_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("compiler,flags", _compiler_params())
def test_hal_ops_are_inlined(compiler, flags, spi_hal_dir):
    """All HAL register/field operations must be fully inlined — no subroutine calls."""
    asm = _compile_to_asm(compiler, flags, spi_hal_dir)

    for func in ("hal_ctrl_get", "hal_ctrl_set", "hal_prescaler_get", "hal_prescaler_set"):
        body = _function_body(asm, func)
        assert body, f"{func} not found in assembly (check driver compilation)"
        assert not _has_call(body), f"{func} contains a subroutine call — abstraction is not zero-cost:\n" + "\n".join(
            body
        )


@pytest.mark.parametrize("compiler,flags", _compiler_params())
def test_register_ops_match_raw_baseline(compiler, flags, spi_hal_dir):
    """HAL register read/write must emit the same number of instructions as raw volatile access."""
    asm = _compile_to_asm(compiler, flags, spi_hal_dir)

    for hal_fn, raw_fn in (
        ("hal_ctrl_get", "raw_ctrl_get"),
        ("hal_ctrl_set", "raw_ctrl_set"),
    ):
        hal_instrs = _function_body(asm, hal_fn)
        raw_instrs = _function_body(asm, raw_fn)
        assert len(hal_instrs) == len(raw_instrs), (
            f"{hal_fn} ({len(hal_instrs)} instrs) vs {raw_fn} ({len(raw_instrs)} instrs)"
            f" — HAL adds overhead\n"
            f"HAL: {hal_instrs}\n"
            f"Raw: {raw_instrs}"
        )
