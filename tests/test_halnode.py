"""Unit tests for HalBaseNode and its subclasses."""

import pytest

from peakrdl_halcpp.halnode import (
    HalAddrmapNode,
    HalFieldNode,
    HalMemNode,
    HalRegfileNode,
    HalRegNode,
)


# ---------------------------------------------------------------------------
# Name properties
# ---------------------------------------------------------------------------


class TestNameProperties:
    def _simple(self, name="my_map"):
        return f"addrmap {name} {{ default regwidth=32; reg {{ field {{sw=rw; hw=r;}} f[7:0]; }} ctrl @0x0; }};"

    def test_inst_name_hal(self, compile_rdl_string):
        top = compile_rdl_string(self._simple())
        assert HalAddrmapNode(top).inst_name_hal == "my_map_hal"

    def test_orig_type_name_hal(self, compile_rdl_string):
        top = compile_rdl_string(self._simple())
        assert HalAddrmapNode(top).orig_type_name_hal == "my_map_hal"


    def test_inst_name_differs_from_type(self, compile_rdl_string):
        rdl = """
        addrmap parent {
            addrmap child_t {
                default regwidth=32;
                reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x0;
            };
            child_t my_inst;
        };
        """
        top = compile_rdl_string(rdl)
        child = list(HalAddrmapNode(top).halchildren(HalAddrmapNode))[0]
        assert child.inst_name_hal == "my_inst_hal"
        assert child.orig_type_name_hal == "child_t_hal"

    def test_orig_type_name_falls_back_to_type_name_for_anonymous(self, compile_rdl_string):
        rdl = "addrmap outer { addrmap { default regwidth=32; reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x0; } anon_inst; };"
        top = compile_rdl_string(rdl)
        child = list(HalAddrmapNode(top).halchildren(HalAddrmapNode))[0]
        # Anonymous types have no orig_type_name; the property falls back to type_name
        assert child.orig_type_name is not None


# ---------------------------------------------------------------------------
# get_docstring
# ---------------------------------------------------------------------------


class TestDocstring:
    _CHILD = "default regwidth=32; reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x0;"

    def test_no_desc_returns_empty(self, compile_rdl_string):
        top = compile_rdl_string(f"addrmap m {{ {self._CHILD} }};")
        assert HalAddrmapNode(top).get_docstring() == ""

    def test_single_line(self, compile_rdl_string):
        top = compile_rdl_string(f'addrmap m {{ desc = "My description."; {self._CHILD} }};')
        assert HalAddrmapNode(top).get_docstring() == "/*\n * My description.\n */"

    def test_multiline(self, compile_rdl_string):
        # RDL has no \n escape; a literal newline inside the string is the correct syntax
        rdl = 'addrmap m { desc = "Line 1.\nLine 2."; ' + self._CHILD + " };"
        top = compile_rdl_string(rdl)
        assert HalAddrmapNode(top).get_docstring() == "/*\n * Line 1.\n * Line 2.\n */"


# ---------------------------------------------------------------------------
# is_bus
# ---------------------------------------------------------------------------


class TestIsBus:
    def test_addrmap_with_only_addrmap_children_is_bus(self, compile_rdl_string):
        rdl = """
        addrmap outer {
            addrmap inner_t {
                default regwidth=32;
                reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x0;
            };
            inner_t inner;
        };
        """
        top = compile_rdl_string(rdl)
        assert HalAddrmapNode(top).is_bus is True

    def test_addrmap_with_reg_is_not_bus(self, compile_rdl_string):
        rdl = "addrmap m { default regwidth=32; reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x0; };"
        top = compile_rdl_string(rdl)
        assert HalAddrmapNode(top).is_bus is False

    def test_non_addrmap_nodes_never_are_bus(self, compile_rdl_string):
        rdl = "addrmap m { default regwidth=32; reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x0; };"
        top = compile_rdl_string(rdl)
        reg = list(HalAddrmapNode(top).halchildren(HalRegNode))[0]
        assert reg.is_bus is False


# ---------------------------------------------------------------------------
# _halfactory
# ---------------------------------------------------------------------------


class TestHalfactory:
    def _top_reg_rdl(self):
        return "addrmap m { default regwidth=32; reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x0; };"

    def test_field_node(self, compile_rdl_string):
        top = compile_rdl_string(self._top_reg_rdl())
        reg = list(HalAddrmapNode(top).halchildren(HalRegNode))[0]
        field = list(reg.halchildren(HalFieldNode))[0]
        assert isinstance(field, HalFieldNode)

    def test_reg_node(self, compile_rdl_string):
        top = compile_rdl_string(self._top_reg_rdl())
        reg = list(HalAddrmapNode(top).halchildren(HalRegNode))[0]
        assert isinstance(reg, HalRegNode)

    def test_addrmap_node(self, compile_rdl_string):
        rdl = """
        addrmap outer {
            addrmap inner_t { default regwidth=32; reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x0; };
            inner_t inner;
        };
        """
        top = compile_rdl_string(rdl)
        child = list(HalAddrmapNode(top).halchildren(HalAddrmapNode))[0]
        assert isinstance(child, HalAddrmapNode)

    def test_mem_node(self, compile_rdl_string):
        rdl = """
        addrmap m {
            mem { memwidth=32; mementries=16; } external m1 @0x0;
        };
        """
        top = compile_rdl_string(rdl)
        mem = list(HalAddrmapNode(top).halchildren(HalMemNode))[0]
        assert isinstance(mem, HalMemNode)

    def test_regfile_node(self, compile_rdl_string):
        rdl = """
        addrmap m {
            regfile rf_t {
                default regwidth=32;
                reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x0;
            };
            rf_t rf @0x0;
        };
        """
        top = compile_rdl_string(rdl)
        rf = list(HalAddrmapNode(top).halchildren(HalRegfileNode))[0]
        assert isinstance(rf, HalRegfileNode)


# ---------------------------------------------------------------------------
# HalFieldNode.cpp_access_type
# ---------------------------------------------------------------------------


class TestFieldAccessType:
    def _top_with_field(self, compile_rdl_string, sw_access: str):
        rdl = f"addrmap m {{ default regwidth=32; reg {{ field {{sw={sw_access}; hw=r;}} f[7:0]; }} ctrl @0x0; }};"
        top = compile_rdl_string(rdl)
        reg = list(HalAddrmapNode(top).halchildren(HalRegNode))[0]
        return list(reg.halchildren(HalFieldNode))[0]

    def test_rw(self, compile_rdl_string):
        assert self._top_with_field(compile_rdl_string, "rw").cpp_access_type == "FieldRW"

    def test_ro(self, compile_rdl_string):
        rdl = "addrmap m { default regwidth=32; reg { field {sw=r; hw=rw;} f[7:0]; } ctrl @0x0; };"
        top = compile_rdl_string(rdl)
        reg = list(HalAddrmapNode(top).halchildren(HalRegNode))[0]
        field = list(reg.halchildren(HalFieldNode))[0]
        assert field.cpp_access_type == "FieldRO"

    def test_wo(self, compile_rdl_string):
        assert self._top_with_field(compile_rdl_string, "w").cpp_access_type == "FieldWO"

    def test_field_address_offset_always_zero(self, compile_rdl_string):
        rdl = "addrmap m { default regwidth=32; reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x40; };"
        top = compile_rdl_string(rdl)
        reg = list(HalAddrmapNode(top).halchildren(HalRegNode))[0]
        field = list(reg.halchildren(HalFieldNode))[0]
        assert field.address_offset == 0


# ---------------------------------------------------------------------------
# HalRegNode properties
# ---------------------------------------------------------------------------


class TestRegProperties:
    def test_reg_access_type_rw(self, compile_rdl_string):
        rdl = "addrmap m { default regwidth=32; reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x0; };"
        top = compile_rdl_string(rdl)
        reg = list(HalAddrmapNode(top).halchildren(HalRegNode))[0]
        assert reg.cpp_access_type == "RegRW"

    def test_reg_access_type_ro(self, compile_rdl_string):
        rdl = "addrmap m { default regwidth=32; reg { field {sw=r; hw=rw;} f[7:0]; } ctrl @0x0; };"
        top = compile_rdl_string(rdl)
        reg = list(HalAddrmapNode(top).halchildren(HalRegNode))[0]
        assert reg.cpp_access_type == "RegRO"

    def test_width_8bit(self, compile_rdl_string):
        rdl = "addrmap m { default regwidth=32; reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x0; };"
        top = compile_rdl_string(rdl)
        reg = list(HalAddrmapNode(top).halchildren(HalRegNode))[0]
        assert reg.width == 8

    def test_width_32bit(self, compile_rdl_string):
        rdl = "addrmap m { default regwidth=32; reg { field {sw=rw; hw=r;} f[31:0]; } ctrl @0x0; };"
        top = compile_rdl_string(rdl)
        reg = list(HalAddrmapNode(top).halchildren(HalRegNode))[0]
        assert reg.width == 32

    def test_address_offset(self, compile_rdl_string):
        rdl = "addrmap m { default regwidth=32; reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x40; };"
        top = compile_rdl_string(rdl)
        reg = list(HalAddrmapNode(top).halchildren(HalRegNode))[0]
        assert reg.address_offset == 0x40


# ---------------------------------------------------------------------------
# HalAddrmapNode properties
# ---------------------------------------------------------------------------


class TestAddrmapProperties:
    _NESTED = """
    addrmap outer {
        addrmap inner_t { default regwidth=32; reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x0; };
        inner_t inner;
    };
    """
    _TOP = "addrmap m { default regwidth=32; reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x0; };"

    def test_is_top_node(self, compile_rdl_string):
        top = compile_rdl_string(self._TOP)
        assert HalAddrmapNode(top).is_top_node is True

    def test_nested_node_is_not_top(self, compile_rdl_string):
        top = compile_rdl_string(self._NESTED)
        child = list(HalAddrmapNode(top).halchildren(HalAddrmapNode))[0]
        assert child.is_top_node is False

    def test_get_template_line_top_has_void_default(self, compile_rdl_string):
        top = compile_rdl_string(self._TOP)
        assert "PARENT_TYPE=void" in HalAddrmapNode(top).get_template_line()

    def test_get_template_line_nested_no_default(self, compile_rdl_string):
        top = compile_rdl_string(self._NESTED)
        child = list(HalAddrmapNode(top).halchildren(HalAddrmapNode))[0]
        assert "PARENT_TYPE=void" not in child.get_template_line()
        assert "PARENT_TYPE" in child.get_template_line()


# ---------------------------------------------------------------------------
# halchildren filtering
# ---------------------------------------------------------------------------


class TestHalchildren:
    def test_type_filter(self, compile_rdl_string):
        rdl = """
        addrmap m {
            default regwidth=32;
            reg { field {sw=rw; hw=r;} f[7:0]; } r1 @0x0;
            reg { field {sw=rw; hw=r;} f[7:0]; } r2 @0x4;
        };
        """
        top = compile_rdl_string(rdl)
        regs = list(HalAddrmapNode(top).halchildren(HalRegNode))
        assert len(regs) == 2
        assert all(isinstance(r, HalRegNode) for r in regs)

    def test_unique_orig_type_deduplicates(self, compile_rdl_string):
        rdl = """
        addrmap m {
            default regwidth=32;
            reg my_reg_t { field {sw=rw; hw=r;} f[7:0]; };
            my_reg_t r1 @0x0;
            my_reg_t r2 @0x4;
        };
        """
        top = compile_rdl_string(rdl)
        hal = HalAddrmapNode(top)
        assert len(list(hal.halchildren(HalRegNode))) == 2
        assert len(list(hal.halchildren(HalRegNode, unique_orig_type=True))) == 1

    def test_haldescendants_reaches_nested(self, compile_rdl_string):
        rdl = """
        addrmap outer {
            addrmap inner_t {
                default regwidth=32;
                reg { field {sw=rw; hw=r;} f[7:0]; } ctrl @0x0;
            };
            inner_t inner;
        };
        """
        top = compile_rdl_string(rdl)
        addrmaps = list(HalAddrmapNode(top).haldescendants(HalAddrmapNode))
        assert len(addrmaps) == 1
        assert addrmaps[0].inst_name == "inner"
