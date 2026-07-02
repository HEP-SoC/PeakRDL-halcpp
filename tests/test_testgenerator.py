"""End-to-end tests for TestGenerator.

TestGenerator emits per-addrmap .cpp executables + a CMakeLists.txt that
downstream users drop into their own build.  These tests verify the generator
end-to-end: file structure, cmake configure, compile, and ctest execution.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from peakrdl_halcpp import HalExporter
from peakrdl_halcpp.test_generator import TestGenerator

RDL_DIR = Path(__file__).parent / "rdl"

_CMAKE = shutil.which("cmake")

pytestmark = pytest.mark.skipif(not _CMAKE, reason="cmake not found in PATH")

CASES = [
    "atxmega_spi.rdl",
    "array_reg.rdl",
]


def _run(args: list, cwd: Path, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)


@pytest.fixture(params=CASES)
def test_output(request, compile_rdl, tmp_path):
    """Generate HAL headers + test project for one RDL file into a temp dir."""
    top = compile_rdl(RDL_DIR / request.param)
    HalExporter().export(node=top, outdir=str(tmp_path))
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    TestGenerator().export(node=top, outdir=str(test_dir))
    return test_dir


def test_generated_structure(test_output):
    """TestGenerator must emit CMakeLists.txt, at least one .cpp, and copy test_utils/."""
    assert (test_output / "CMakeLists.txt").exists(), "Missing generated CMakeLists.txt"
    assert list(test_output.glob("*.cpp")), "No .cpp test files generated"
    assert (test_output / "test_utils").is_dir(), "Missing test_utils/ directory"
    for header in ("test_utils.h", "mock_io.h", "reg_test_utils.h", "field_test_utils.h"):
        assert (test_output / "test_utils" / header).exists(), f"Missing test_utils/{header}"


def test_generated_tests_compile_and_pass(test_output):
    """Generated test project must configure, build, and all ctest cases must pass."""
    build_dir = test_output.parent / "build"

    configure = _run(
        [_CMAKE, "-S", str(test_output), "-B", str(build_dir), "-DCMAKE_CXX_STANDARD=17"],
        cwd=test_output,
    )
    assert configure.returncode == 0, f"cmake configure failed:\n{configure.stderr}"

    build = _run([_CMAKE, "--build", str(build_dir)], cwd=build_dir)
    assert build.returncode == 0, f"cmake build failed:\n{build.stderr}"

    result = _run(["ctest", "--output-on-failure"], cwd=build_dir)
    assert result.returncode == 0, f"ctest failed:\n{result.stdout}\n{result.stderr}"
