import os
from typing import Union, Any, List, Dict
import shutil
from itertools import chain
import logging

import jinja2 as jj
from systemrdl.node import RootNode, AddrmapNode

from .halutils import *
from .halnode import *

class HalExporter():
    """HAL C++ PeakRDL plugin top class to generate the C++ HAL from SystemRDL description.

    Class methods:

    - :func:`copy_base_headers`
    - :func:`export`
    - :func:`process_template`
    """

    def __init__(self, **kwargs: Any):
        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" %
                            list(kwargs.keys())[0])

        #: HAL C++ copied header library location within the generated files output directory
        self.cpp_dir = "include"

        filetype = "*.h"
        abspaths = os.path.join(os.path.dirname(__file__), self.cpp_dir)
        #: HAL C++ headers list (copied into :attr:`~cpp_dir`)
        self.base_headers = [f for f in os.listdir(
            abspaths) if f.endswith(filetype[1:])]

    def copy_base_headers(self, outdir: str):
        """Copies the HAL C++ headers to the generated files location given
        by the outdir parameter.

        Parameters
        ----------
        outdir: str
            Output directory in which the output files are generated.
        """
        abspaths = [os.path.join(os.path.dirname(
            __file__), self.cpp_dir, x) for x in self.base_headers]
        outdir = os.path.join(outdir, "include")
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        [shutil.copy(x, outdir) for x in abspaths]

    def export(self,
               node: 'AddrmapNode',
               outdir: str,
               list_files: bool = False,
               ext_modules: List = [str],
               skip_buses: bool = False
               ):
        """Main function of the plugin extension.

        Parameters
        ----------
        node: AddrmapNode
            Top AddrmapNode of the SystemRDL description.
        outdir: str
            Output directory in which the output files are generated.
        list_files: bool = False
            Don't generate but print the files that would be generated.
        ext_modules: List[str]
            List of modules (i.e., SystemRDL addrmap objects) with extended functionalities.
        skip_buses: bool = False
            Keep AddrMapNodes containing only AddrMapNodes.
        """

        # Check the node is an AddrmapNode object
        if not isinstance(node, AddrmapNode):
            raise TypeError(
                "'node' argument expects type AddrmapNode. Got '%s'" % type(node).__name__)

        halutils = HalUtils(ext_modules)

        # Create top HalAddrmapNode from top AddrmapNode
        top = HalAddrmapNode(node)

        if not list_files:
            # Create the output directory for the generated files
            try:
                os.makedirs(outdir)
            except FileExistsError:
                pass

            # Copy the base header files (fixed code) to the output directory
            self.copy_base_headers(outdir)

        # Iterate over all the decendants of the top HalAddrmap object
        concatenated_iterable = chain(top.haldescendants(
            descendants_type=HalAddrmapNode, skip_buses=skip_buses, unique_orig_type=True), top)

        if list_files:
            print('INFO: Only listing files (no actual generation)')

        for halnode in concatenated_iterable:
            # Create the context for the template generation
            context = {
                'halnode': halnode,
                'halutils': halutils,
                'skip_buses': skip_buses,
                'HalAddrmapNode': HalAddrmapNode,
                'HalMemNode': HalMemNode,
                'HalRegfileNode': HalRegfileNode,
                'HalRegNode': HalRegNode,
                'HalFieldNode': HalFieldNode,
            }

            # The next lines generate the C++ header file for the
            # HalAddrmap node using a jinja2 template.
            text = self.process_template(context)

            # All addrmaps use the original type name (not instance name)
            # This ensures include statements match the actual filenames
            out_file = os.path.join(
                outdir, halnode.orig_type_name_hal.lower() + ".h")

            # Generate the files if --list-files parameter is not set
            if list_files:
                print('INFO: ' + out_file)
            else:
                print('INFO: Generated file: ' + out_file)
                with open(out_file, 'w') as f:
                    f.write(text)

    def process_template(self, context: Dict) -> str:
        """Generates a C++ header file based on a jinja2 template.

        Parameters
        ----------
        context: Dict
            Dictionary containing a HalAddrmapNode and the HalUtils object
            (and other variables) passed to the jinja2 env

        Returns
        -------
        str
            Text of the generated C++ header for a given HalAddrmap node.
        """
        # Create a jinja2 env with the template contained in the templates
        # folder located in the same directory than this file
        env = jj.Environment(
            loader=jj.FileSystemLoader(
                '%s/templates/' % os.path.dirname(__file__)),
            trim_blocks=True,
            lstrip_blocks=True)
        # Add the base zip function to the env
        env.filters.update({
            'zip': zip,
        })
        # Render the C++ header text using the jinja2 template and the
        # specific context
        cpp_header_text = env.get_template("addrmap.h.j2").render(context)
        return cpp_header_text
