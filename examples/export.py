from systemrdl import RDLCompiler
from systemrdl.node import AddrmapNode

from peakrdl_halcpp import HalExporter

rdl_files = ["atxmega_spi.rdl", "regs_and_mem.rdl"]

for rdl_file in rdl_files:
    rdlc = RDLCompiler()
    rdlc.compile_file(rdl_file)

    root = rdlc.elaborate()

    top: AddrmapNode | None = None
    for child in root.children(unroll=True):
        if isinstance(child, AddrmapNode):
            top = child
    if top is None:
        raise ValueError

    exporter = HalExporter()

    exporter.export(
        node=top,
        outdir="generated",
    )
