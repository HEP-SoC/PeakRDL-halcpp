import os
import tempfile
from pathlib import Path

import pytest
from systemrdl import RDLCompiler
from systemrdl.node import AddrmapNode


def pytest_addoption(parser):
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Regenerate golden output files in tests/expected/",
    )


@pytest.fixture
def update_golden(request):
    return request.config.getoption("--update-golden")


@pytest.fixture
def compile_rdl():
    def _compile(rdl_file: Path) -> AddrmapNode:
        rdlc = RDLCompiler()
        rdlc.compile_file(str(rdl_file))
        root = rdlc.elaborate()
        return root.children(unroll=True)[0]

    return _compile


@pytest.fixture
def compile_rdl_string():
    def _compile(rdl_src: str) -> AddrmapNode:
        rdlc = RDLCompiler()
        with tempfile.NamedTemporaryFile(suffix=".rdl", mode="w", delete=False) as f:
            f.write(rdl_src)
            fname = f.name
        try:
            rdlc.compile_file(fname)
            root = rdlc.elaborate()
        finally:
            os.unlink(fname)
        return root.children(unroll=True)[0]

    return _compile
