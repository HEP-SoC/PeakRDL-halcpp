from typing import TYPE_CHECKING, Optional, Iterator, List
import itertools
import logging

from systemrdl.node import Node, RootNode, AddrmapNode, MemNode, RegfileNode
from systemrdl.node import RegNode, FieldNode, SignalNode, AddressableNode


if TYPE_CHECKING:
    from systemrdl.compiler import RDLEnvironment

# Logger generation for halnode module
halnode_logger = logging.getLogger("halnode_logger")
# Console handler
ch = logging.StreamHandler()
# create formatter and add it to the handlers
formatter = logging.Formatter('%(name)s - %(levelname)s: %(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
halnode_logger.addHandler(ch)


class HalBaseNode(Node):
    """HAL node base class.

    This class inherits from the systemrdl Node class. Each subclass will also inherit
    its systemrdl Node subclass specialization counterpart (e.g, HalFieldNode inherits
    from FieldNode).

    .. inheritance-diagram:: peakrdl_halcpp.halnode.HalAddrmapNode
                             peakrdl_halcpp.halnode.HalRegNode
                             peakrdl_halcpp.halnode.HalMemNode
                             peakrdl_halcpp.halnode.HalRegfileNode
                             peakrdl_halcpp.halnode.HalFieldNode
        :top-classes: HalBaseNode
        :parts: 1

    Class methods:

        - :func:`get_docstring`
        - :func:`_halfactory`
        - :func:`halunrolled`
        - :func:`halchildren`
        - :func:`haldescendants`
    """

    # Static variable to retain warning issued
    _type_warning_list: List[str] = []

    def __iter__(self):
        # Make this class iterable
        yield self

    @property
    def inst_name_hal(self) -> str:
        """Return the node name with the '_hal' suffix."""
        return super().inst_name.lower() + "_hal"

    @property
    def orig_type_name_hal(self) -> str:
        """Return the original type name with the '_hal' suffix."""
        return super().orig_type_name.lower() + "_hal"

    @property
    def orig_type_name(self) -> str:
        """Returns type_name if orig_type_name is none.

        Node instantiate anonymously do not have orig_type_name so use type_name.
        """
        if super().orig_type_name is not None:
            return super().orig_type_name
        else:
            return super().type_name

    @property
    def is_bus(self) -> bool:
        """Returns True if the HAL node is considered a bus (i.e., an addrmap containing only addrmaps).

        Always returns False for non-addrmap nodes. Overridden in :class:`HalAddrmapNode`.
        """
        return False

    def get_docstring(self) -> str:
        """Converts the node description property into a C++ multi-line comment.

        Returns
        -------
        str
            A ``/* ... */`` formatted comment containing the node's ``desc`` property,
            or an empty string if no description is set.
        """
        desc = "/*\n"
        if self.get_property('desc') is not None:
            for l in self.get_property('desc').splitlines():
                desc = desc + " * " + l + "\n"
            return desc + " */"
        return ""

    @staticmethod
    def _halfactory(inst: Node, env: 'RDLEnvironment', parent: Optional['Node'] = None) -> Optional['Node']:
        """Factory method that wraps a systemrdl Node in its corresponding HAL subclass.

        Adapted from the systemrdl Node factory. Returns ``None`` for unsupported
        node types (e.g., :class:`~systemrdl.node.SignalNode`).

        Parameters
        ----------
        inst : Node
            The systemrdl node instance to wrap.
        env : RDLEnvironment
            The systemrdl compilation environment.
        parent : Node, optional
            The parent node.

        Returns
        -------
        Node or None
            The wrapped HAL node, or ``None`` if the node type is not supported.
        """
        if isinstance(inst, FieldNode):
            return HalFieldNode(inst)
        elif isinstance(inst, RegNode):
            return HalRegNode(inst)
        elif isinstance(inst, RegfileNode):
            return HalRegfileNode(inst)
        elif isinstance(inst, AddrmapNode):
            return HalAddrmapNode(inst)
        elif isinstance(inst, MemNode):
            return HalMemNode(inst)
        elif isinstance(inst, SignalNode):
            # Signals are not supported by this plugin
            return None
        else:
            halnode_logger.error(f'inst type {type(inst)} is not recognized')
            raise RuntimeError

    def halunrolled(self) -> Iterator['Node']:
        """Yields one HAL node per array element, or yields the node itself if not an array.

        Adapted from the systemrdl Node unrolling logic. For array nodes, each yielded
        node has its ``current_idx`` set to the corresponding index tuple.
        """
        cls = type(self)
        if isinstance(self, AddressableNode) and self.is_array:  # pylint: disable=no-member
            # Is an array. Yield a Node object for each instance
            range_list = [
                range(n) for n in self.array_dimensions]  # pylint: disable=no-member
            for idxs in itertools.product(*range_list):
                N = cls(self)
                N.current_idx = idxs  # type: ignore
                yield N
        else:
            # Not an array. Nothing to unroll
            yield cls(self.inst, self.env, self.parent)

    def halchildren(self,
                    children_type: 'Node' = Node,
                    unroll: bool = False,
                    skip_not_present: bool = True,
                    skip_buses: bool = False,
                    bus_offset: int = 0,
                    unique_orig_type: bool = False,
                    type_dict: Optional[dict] = None
                    ) -> Iterator['Node']:
        """Yields HAL-wrapped children of this node, with optional filtering.

        Wraps systemrdl ``Node.children`` so that each child is converted to the
        appropriate HAL subclass via :func:`_halfactory`.

        Parameters
        ----------
        children_type : Node, optional
            Only yield children that are instances of this type. Defaults to :class:`~systemrdl.node.Node`
            (all types).
        unroll : bool, optional
            If True, unroll array children into individual element nodes.
        skip_not_present : bool, optional
            If True (default), skip nodes whose ``ispresent`` property is False.
        skip_buses : bool, optional
            If True, transparent bus addrmaps (containing only addrmaps) are
            flattened and their children are yielded instead.
        bus_offset : int, optional
            Cumulative address offset inherited from skipped bus nodes.
        unique_orig_type : bool, optional
            If True, yield at most one child per unique ``orig_type_name``.
        type_dict : dict, optional
            Dictionary used internally to track seen ``orig_type_name`` values and
            detect parameterised type conflicts. Pass ``None`` to start fresh.
        """

        if type_dict is None:
            type_dict = {}

        for child in self.children(unroll, skip_not_present):
            halchild = HalBaseNode._halfactory(child, self.env, self)
            if isinstance(halchild, children_type):
                child_bus_offset = 0
                if skip_buses and halchild.is_bus:
                    child_bus_offset = bus_offset + halchild.address_offset
                    yield from halchild.halchildren(children_type, unroll, skip_not_present, skip_buses, child_bus_offset, unique_orig_type, type_dict)
                else:
                    halchild.bus_offset = bus_offset
                    if not unique_orig_type or halchild.orig_type_name not in type_dict:
                        yield halchild

                # Issue a warning if orig_type_name already encountered and type_name does not match
                if halchild.orig_type_name in type_dict:
                    if type_dict[halchild.orig_type_name] != halchild.type_name and halchild.orig_type_name not in HalBaseNode._type_warning_list:
                        halnode_logger.warning(f'Two instances with same orig_type_name but different type_name (i.e., parameters) detected.')
                        halnode_logger.warning(f'Original type name is: {halchild.orig_type_name}')
                        halnode_logger.warning(f'Type name 1 is: {type_dict[halchild.orig_type_name]}')
                        halnode_logger.warning(f'Type name 2 is: {halchild.type_name}')
                        halnode_logger.warning(f'This is not properly supported by this plugin and might create inconsistent output.')
                        # Add it to the list to avoid repeating the warning
                        HalBaseNode._type_warning_list.append(
                            halchild.orig_type_name)
                elif halchild.orig_type_name is not None:
                    type_dict[halchild.orig_type_name] = halchild.type_name

    def haldescendants(self,
                       descendants_type: 'Node' = Node,
                       unroll: bool = False,
                       skip_not_present: bool = True,
                       in_post_order: bool = False,
                       skip_buses: bool = False,
                       bus_offset: int = 0,
                       unique_orig_type: bool = False,
                       type_dict: Optional[dict] = None
                       ) -> Iterator['Node']:
        """Yields all HAL-wrapped descendants of this node, with optional filtering.

        Adapted from systemrdl ``Node.descendants``. Recursively calls
        :func:`halchildren` to traverse the full subtree.

        Parameters
        ----------
        descendants_type : Node, optional
            Only yield descendants that are instances of this type. Defaults to
            :class:`~systemrdl.node.Node` (all types).
        unroll : bool, optional
            If True, unroll array nodes into individual element nodes.
        skip_not_present : bool, optional
            If True (default), skip nodes whose ``ispresent`` property is False.
        in_post_order : bool, optional
            If True, yield children before their parent (post-order traversal).
            Defaults to pre-order.
        skip_buses : bool, optional
            If True, transparent bus addrmaps are flattened and their children
            are yielded instead.
        bus_offset : int, optional
            Cumulative address offset inherited from skipped bus nodes.
        unique_orig_type : bool, optional
            If True, yield at most one descendant per unique ``orig_type_name``.
        type_dict : dict, optional
            Dictionary used internally to track seen ``orig_type_name`` values.
            Pass ``None`` to start fresh.
        """

        for child in self.halchildren(descendants_type, unroll, skip_not_present, skip_buses, bus_offset, unique_orig_type, type_dict):
            if isinstance(child, descendants_type):
                child_bus_offset = 0
                if skip_buses and self.is_bus:
                    child_bus_offset = bus_offset + child.address_offset

                if in_post_order:
                    yield from child.haldescendants(descendants_type, unroll, skip_not_present, in_post_order, skip_buses, child_bus_offset, unique_orig_type, type_dict)

                if not (skip_buses and child.is_bus):
                    yield child

                if not in_post_order:
                    yield from child.haldescendants(descendants_type, unroll, skip_not_present, in_post_order, skip_buses, child_bus_offset, unique_orig_type, type_dict)


class HalFieldNode(HalBaseNode, FieldNode):
    """HalFieldNode class inheriting from HalBaseNode class and systemrdl FieldNode class.

        Class methods:

        - :func:`get_enums`
    """

    def __init__(self, node: FieldNode):
        # Use the system-RDL AddrmapNode class initialization
        super().__init__(node.inst, node.env, node.parent)

    @property
    def address_offset(self) -> int:
        """Always returns 0. Fields have no independent address; the offset is on the parent register."""
        return 0

    @property
    def cpp_access_type(self) -> str:
        """C++ access right template selection."""
        if self.is_sw_readable and self.is_sw_writable:
            return "FieldRW"
        elif self.is_sw_writable and not self.is_sw_readable:
            return "FieldWO"
        elif self.is_sw_readable:
            return "FieldRO"
        else:
            raise ValueError(f'Node field access rights are not found \
                              {self.inst.inst_name}')

    def get_enums(self):
        """Returns the enumeration(s) of a FieldNode.

        Inside an addrmap node, all enumerations must have a different name.
        The jinja template used to create the C++ header filters enumerations
        with already-existing names.

        Returns
        -------
        tuple
            ``(has_enum, enum_cls_name, enum_strings, enum_values, enum_desc, const_width)``
            where ``has_enum`` is a bool indicating whether an encoding is defined.
            All other elements are ``None`` when ``has_enum`` is False.
        """
        encode = self.get_property('encode')
        if encode is not None:
            enum_cls_name = encode.type_name
            enum_strings = []
            enum_values = []
            enum_desc = []
            for k in encode.members:
                enum_strings.append(encode.members[k].name)
                enum_values.append(encode.members[k].value)
                enum_desc.append(encode.members[k].rdl_desc)

            const_width = max(enum_values).bit_length()

            return True, enum_cls_name, enum_strings, enum_values, enum_desc, const_width

        return False, None, None, None, None, None


class HalRegNode(HalBaseNode, RegNode):
    """HAL node wrapping a SystemRDL register (:class:`~systemrdl.node.RegNode`).

    Inherits from :class:`HalBaseNode` and :class:`~systemrdl.node.RegNode`.

    Class methods:

    - :func:`get_template_line`
    - :func:`get_cls_tmpl_params`
    """

    def __init__(self, node: RegNode):
        # Use the system-RDL AddrmapNode class initialization
        super().__init__(node.inst, node.env, node.parent)

        self.bus_offset = 0

    @property
    def cpp_access_type(self):
        """C++ access right template selection."""
        if self.has_sw_readable and self.has_sw_writable:
            return "RegRW"
        elif self.has_sw_writable and not self.has_sw_readable:
            return "RegWO"
        elif self.has_sw_readable:
            return "RegRO"
        assert False

    @property
    def address_offset(self) -> int:
        """Returns the address offset adjusted by the accumulated bus offset.

        For array registers with no current index set, the offset of the first
        element is used.
        """
        if self.is_array and self.current_idx is None:
            return self.bus_offset + next(self.halunrolled()).address_offset
        else:
            return self.bus_offset + super().address_offset

    @property
    def width(self) -> int:
        """Returns the register width in bits, derived from the highest bit position of its fields."""
        return max([c.high for c in self.halchildren(HalFieldNode)]) + 1

    def get_template_line(self) -> str:
        """Returns the class template string."""
        return f"template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>"

    def get_cls_tmpl_params(self) -> str:
        """Returns the class template parameter string.

        These parameters must match the the template returned by :func:`get_template_line`.
        """
        return "<BASE, WIDTH, PARENT_TYPE>"


class HalRegfileNode(HalBaseNode, RegfileNode):
    """HAL node wrapping a SystemRDL register file (:class:`~systemrdl.node.RegfileNode`).

    Inherits from :class:`HalBaseNode` and :class:`~systemrdl.node.RegfileNode`.

    Class methods:

    - :func:`get_template_line`
    - :func:`get_cls_tmpl_params`
    """

    def __init__(self, node: RegfileNode):
        # Use the system-RDL AddrmapNode class initialization
        super().__init__(node.inst, node.env, node.parent)

        self.bus_offset = 0

    @property
    def cpp_access_type(self):
        """C++ access right template selection.

        For RegfileNodes, the access rights are selected at lower
        levels (e.g., registers).
        """
        return "RegfileNode"

    @property
    def address_offset(self) -> int:
        """Returns the address offset adjusted by the accumulated bus offset.

        For array register files with no current index set, the offset of the
        first element is used.
        """
        if self.is_array and self.current_idx is None:
            return self.bus_offset + next(self.halunrolled()).address_offset
        else:
            return self.bus_offset + super().address_offset

    def get_template_line(self) -> str:
        """Returns the class template string."""
        return f"template <uint32_t BASE, typename PARENT_TYPE>"

    def get_cls_tmpl_params(self) -> str:
        """Returns the class template parameter string.

        These parameters must match the the template returned by :func:`get_template_line`.
        """
        return "<BASE, PARENT_TYPE>"


class HalMemNode(HalBaseNode, MemNode):
    """HAL node wrapping a SystemRDL memory (:class:`~systemrdl.node.MemNode`).

    Inherits from :class:`HalBaseNode` and :class:`~systemrdl.node.MemNode`.

    Class methods:

    - :func:`get_template_line`
    - :func:`get_cls_tmpl_params`
    """

    def __init__(self, node: MemNode):
        # Use the system-RDL MemNode class initialization
        super().__init__(node.inst, node.env, node.parent)

        self.bus_offset = 0

    @property
    def address_offset(self) -> int:
        """Returns the address offset adjusted by the accumulated bus offset."""
        return self.bus_offset + super().address_offset

    def get_template_line(self) -> str:
        """Returns the class template string."""
        return f"template <uint32_t BASE, uint32_t SIZE, typename PARENT_TYPE>"

    def get_cls_tmpl_params(self) -> str:
        """Returns the class template parameter string.

        These parameters must match the the template returned by :func:`get_template_line`.
        """
        return "<BASE, SIZE, PARENT_TYPE>"


class HalAddrmapNode(HalBaseNode, AddrmapNode):
    """HAL node wrapping a SystemRDL address map (:class:`~systemrdl.node.AddrmapNode`).

    Inherits from :class:`HalBaseNode` and :class:`~systemrdl.node.AddrmapNode`.

    Class methods:

    - :func:`get_template_line`
    - :func:`get_cls_tmpl_params`
    """

    def __init__(self, node: AddrmapNode):
        # Use the system-RDL AddrmapNode class initialization
        super().__init__(node.inst, node.env, node.parent)
        #: The bus offset is used for address offset correction when the --skip-buses option is used
        self.bus_offset = 0

    @property
    def is_top_node(self) -> bool:
        """Checks if this is the top node."""
        return isinstance(self.parent, RootNode)

    @property
    def address_offset(self) -> int:
        """Returns the address offset adjusted by the accumulated bus offset."""
        return self.bus_offset + super().address_offset

    @property
    def is_bus(self) -> bool:
        """Returns True if this addrmap contains only other addrmaps (i.e., is a transparent bus)."""
        for child in self.halchildren():
            if not isinstance(child, HalAddrmapNode):
                return False
        return True

    @property
    def is_mem_addrmap(self) -> bool:
        """Returns True if this addrmap contains only :class:`HalMemNode` children."""
        for child in self.halchildren():
            if not isinstance(child, HalMemNode):
                return False
        return True

    def get_template_line(self) -> str:
        """Returns the class template string."""
        if self.is_top_node:
            # Parent is set to void by default for the top node
            return "template <uint32_t BASE, typename PARENT_TYPE=void>"
        return "template <uint32_t BASE, typename PARENT_TYPE>"

    def get_cls_tmpl_params(self) -> str:
        """Returns the class template parameter string.

        These parameters must match the the template returned by :func:`get_template_line`.
        """
        return "<BASE, PARENT_TYPE>"
