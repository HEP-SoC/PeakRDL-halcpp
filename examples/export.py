from systemrdl import RDLCompiler
from peakrdl_halcpp import HalExporter

rdl_files = ["atxmega_spi.rdl", "regs_and_mem.rdl"]

for rdl_file in rdl_files:
    rdlc = RDLCompiler()
    rdlc.compile_file(rdl_file)

    root = rdlc.elaborate()
    top_gen = root.children(unroll=True)

    top = None
    for top in top_gen:
        top = top
    assert top is not None

    exporter = HalExporter()

    exporter.export(
            node=top,
            outdir="generated",
            )
