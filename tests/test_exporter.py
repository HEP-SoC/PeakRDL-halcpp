from peakrdl_halcpp import HalExporter


def test_import():
    assert HalExporter is not None


def test_instantiation():
    exporter = HalExporter()
    assert exporter is not None
