"""Edge-case unit tests: bus flattening, enumerations, array registers, HalUtils."""

from __future__ import annotations

from peakrdl_halcpp.halnode import HalAddrmapNode, HalFieldNode, HalRegNode
from peakrdl_halcpp.halutils import HalUtils

# ---------------------------------------------------------------------------
# Transparent-bus flattening (skip_buses)
# ---------------------------------------------------------------------------


class TestBusFlattening:
    _BUS_RDL = """
    addrmap outer {
        default regwidth = 32;

        reg { field {sw=rw; hw=r;} ctrl[31:0]; } top_ctrl @0x0;

        addrmap bus_t {
            addrmap leaf_t {
                reg { field {sw=rw; hw=r;} data[31:0]; } data_reg @0x0;
            };
            leaf_t leaf;
        };

        bus_t bus_inst @0x100;
    };
    """

    def test_bus_inst_visible_without_skip(self, compile_rdl_string):
        top = compile_rdl_string(self._BUS_RDL)
        children = list(HalAddrmapNode(top).halchildren())
        names = [c.inst_name for c in children]
        assert "bus_inst" in names

    def test_bus_replaced_by_leaf_with_skip(self, compile_rdl_string):
        top = compile_rdl_string(self._BUS_RDL)
        children = list(HalAddrmapNode(top).halchildren(skip_buses=True))
        names = [c.inst_name for c in children]
        assert "bus_inst" not in names
        assert "leaf" in names

    def test_leaf_address_adjusted_by_bus_offset(self, compile_rdl_string):
        top = compile_rdl_string(self._BUS_RDL)
        children = list(HalAddrmapNode(top).halchildren(skip_buses=True))
        leaf = next(c for c in children if c.inst_name == "leaf")
        # bus_inst @0x100 + leaf @0x0 inside bus → effective 0x100
        assert leaf.address_offset == 0x100

    def test_is_bus_true_for_bus_addrmap(self, compile_rdl_string):
        top = compile_rdl_string(self._BUS_RDL)
        bus_inst = next(c for c in HalAddrmapNode(top).halchildren(HalAddrmapNode) if c.inst_name == "bus_inst")
        assert bus_inst.is_bus is True

    def test_is_bus_false_for_leaf(self, compile_rdl_string):
        top = compile_rdl_string(self._BUS_RDL)
        # traverse into bus_inst to reach leaf
        bus_inst = next(c for c in HalAddrmapNode(top).halchildren(HalAddrmapNode) if c.inst_name == "bus_inst")
        leaf = next(iter(bus_inst.halchildren(HalAddrmapNode)))
        assert leaf.is_bus is False


# ---------------------------------------------------------------------------
# Field enumerations
# ---------------------------------------------------------------------------


class TestEnumerations:
    _ENUM_RDL = """
    addrmap m {
        default regwidth = 32;

        reg {
            enum mode_e {
                OFF  = 2'b00 { desc = "Off"; };
                ON   = 2'b01 { desc = "On"; };
                IDLE = 2'b10 { desc = "Idle"; };
            };

            field { encode = mode_e; sw=rw; hw=r; } mode[1:0] = 0;
            field { sw=rw; hw=r; } en[2:2] = 0;
        } ctrl @0x0;
    };
    """

    def test_field_with_enum_has_encoding(self, compile_rdl_string):
        top = compile_rdl_string(self._ENUM_RDL)
        reg = next(iter(HalAddrmapNode(top).halchildren(HalRegNode)))
        fields = list(reg.halchildren(HalFieldNode))
        mode_field = next(f for f in fields if f.inst_name == "mode")

        has_enum, name, strings, values, _desc, width = mode_field.get_enums()
        assert has_enum is True
        assert name == "mode_e"
        assert strings == ["OFF", "ON", "IDLE"]
        assert values == [0, 1, 2]
        assert width == 2  # max(0,1,2).bit_length() = 2

    def test_field_without_enum_returns_false(self, compile_rdl_string):
        top = compile_rdl_string(self._ENUM_RDL)
        reg = next(iter(HalAddrmapNode(top).halchildren(HalRegNode)))
        fields = list(reg.halchildren(HalFieldNode))
        en_field = next(f for f in fields if f.inst_name == "en")

        has_enum, *rest = en_field.get_enums()
        assert has_enum is False
        assert all(v is None for v in rest)


# ---------------------------------------------------------------------------
# Array registers
# ---------------------------------------------------------------------------


class TestArrayRegisters:
    _ARRAY_RDL = """
    addrmap m {
        default regwidth = 32;

        reg chan_t { field {sw=rw; hw=r;} data[31:0]; };
        chan_t channel[4] @0x0;
    };
    """

    def test_array_reg_is_array(self, compile_rdl_string):
        top = compile_rdl_string(self._ARRAY_RDL)
        reg = next(iter(HalAddrmapNode(top).halchildren(HalRegNode)))
        assert reg.is_array is True

    def test_array_reg_dimensions(self, compile_rdl_string):
        top = compile_rdl_string(self._ARRAY_RDL)
        reg = next(iter(HalAddrmapNode(top).halchildren(HalRegNode)))
        assert reg.array_dimensions == [4]

    def test_halunrolled_yields_one_per_element(self, compile_rdl_string):
        top = compile_rdl_string(self._ARRAY_RDL)
        reg = next(iter(HalAddrmapNode(top).halchildren(HalRegNode)))
        unrolled = list(reg.halunrolled())
        assert len(unrolled) == 4

    def test_array_stride(self, compile_rdl_string):
        top = compile_rdl_string(self._ARRAY_RDL)
        reg = next(iter(HalAddrmapNode(top).halchildren(HalRegNode)))
        # 32-bit register → default stride = 4 bytes
        assert reg.array_stride == 4


# ---------------------------------------------------------------------------
# HalUtils
# ---------------------------------------------------------------------------


class TestHalUtils:
    def _make_node(self, compile_rdl_string, name="my_module"):
        rdl = f"""
        addrmap {name} {{
            default regwidth=32;
            reg {{ field {{sw=rw; hw=r;}} f[7:0]; }} ctrl @0x0;
        }};
        """
        top = compile_rdl_string(rdl)
        return HalAddrmapNode(top)

    def test_has_extern_false_when_no_ext_modules(self, compile_rdl_string):
        node = self._make_node(compile_rdl_string)
        assert HalUtils(ext_modules=None).has_extern(node) is False

    def test_has_extern_false_when_not_in_list(self, compile_rdl_string):
        node = self._make_node(compile_rdl_string)
        assert HalUtils(ext_modules=["other_module"]).has_extern(node) is False

    def test_has_extern_true_when_in_list(self, compile_rdl_string):
        node = self._make_node(compile_rdl_string, name="my_module")
        assert HalUtils(ext_modules=["my_module"]).has_extern(node) is True

    def test_get_include_file_standard(self, compile_rdl_string):
        node = self._make_node(compile_rdl_string, name="my_module")
        result = HalUtils(ext_modules=None).get_include_file(node)
        assert result == "my_module_hal.h"

    def test_get_include_file_ext(self, compile_rdl_string):
        node = self._make_node(compile_rdl_string, name="my_module")
        result = HalUtils(ext_modules=["my_module"]).get_include_file(node)
        assert result == "my_module_hal_ext.h"

    def test_get_extern_standard(self, compile_rdl_string):
        node = self._make_node(compile_rdl_string, name="my_module")
        result = HalUtils(ext_modules=None).get_extern(node)
        assert result == "my_module_hal"

    def test_generate_file_header_contains_url(self):
        header = HalUtils().generate_file_header()
        assert "PeakRD" in header
        assert header.startswith("//")
