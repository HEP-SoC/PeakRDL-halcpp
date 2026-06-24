from typing import List

from .halnode import HalAddrmapNode


class HalUtils():
    """Utility helpers used by the jinja2 template during C++ header generation.

    Class methods:

    - :func:`get_include_file`
    - :func:`has_extern`
    - :func:`get_extern`
    - :func:`generate_file_header`
    """

    def __init__(self, ext_modules: List[str]) -> None:
        """
        Parameters
        ----------
        ext_modules : List[str]
            List of addrmap instance names that have user-supplied ``*_hal_ext.h``
            extension headers.
        """
        #: List of modules (i.e., SystemRDL addrmap objects) with extended functionalities.
        self.ext_modules = ext_modules

    def get_include_file(self, halnode: HalAddrmapNode) -> str:
        """Returns the header filename to ``#include`` for a given HAL node.

        If the node has an extension header, returns ``<name>_hal_ext.h``;
        otherwise returns ``<name>_hal.h``.

        Parameters
        ----------
        halnode : HalAddrmapNode
            The HAL addrmap node whose include filename is needed.

        Returns
        -------
        str
            Header filename (without path).
        """
        has_extern = self.has_extern(halnode)
        return halnode.orig_type_name_hal + "_ext.h" if has_extern else halnode.orig_type_name_hal + ".h"

    def has_extern(self, halnode: HalAddrmapNode) -> bool:
        """Returns True if the HAL node has a user-supplied extension header.

        Parameters
        ----------
        halnode : HalAddrmapNode
            The HAL addrmap node to check.

        Returns
        -------
        bool
            True if ``halnode.inst_name`` appears in :attr:`ext_modules`.
        """
        if self.ext_modules is not None:
            if halnode.inst_name in self.ext_modules:
                return True
        return False

    def get_extern(self, halnode: HalAddrmapNode) -> str:
        """Returns the C++ type name for the node, using the ``_ext`` variant when applicable.

        If the node has an extension header, the ``_hal`` suffix of the original
        type name is replaced by ``_ext``; otherwise the standard ``_hal`` name is
        returned.

        Parameters
        ----------
        halnode : HalAddrmapNode
            The HAL addrmap node.

        Returns
        -------
        str
            C++ type name string (``<name>_ext`` or ``<name>_hal``).
        """
        if self.has_extern(halnode):
            return halnode.orig_type_name.replace('_hal', '_ext')
        return halnode.orig_type_name_hal

    def generate_file_header(self) -> str:
        """Returns a one-line C++ comment used as the header of every generated file.

        Returns
        -------
        str
            A ``// Generated with ...`` comment string.
        """
        comment = f"// Generated with PeakRD-halcpp : https://github.com/Risto97/PeakRDL-halcpp\n"
        return comment
