from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

from peakrdl.plugins.exporter import ExporterSubcommandPlugin

from peakrdl_halcpp.test_generator import TestGenerator  # pylint: disable=import-error

from .exporter import HalExporter

if TYPE_CHECKING:
    import argparse

    from systemrdl.node import AddrmapNode


class Exporter(ExporterSubcommandPlugin):
    """PeakRDL plugin entry point for the halcpp exporter.

    Registers the ``halcpp`` subcommand with PeakRDL and wires it to
    :class:`~peakrdl_halcpp.exporter.HalExporter`.
    """

    short_desc = "Generates C++ Hardware Abstraction Layer (HAL) libraries."
    long_desc = "Generates C++ Hardware Abstraction Layer (HAL) libraries."

    def add_exporter_arguments(self, arg_group: argparse._ActionsContainer) -> None:
        """Registers halcpp-specific CLI arguments with the PeakRDL argument parser.

        Parameters
        ----------
        arg_group : argparse._ActionsContainer
            Argument group provided by PeakRDL into which arguments are added.
        """
        arg_group.add_argument(
            "--ext",
            nargs="*",
            help="List of addrmap modules that have implemented <name>_HAL_EXT class in \
                <name>_hal_ext.h header file, used for extending functionality.",
        )

        arg_group.add_argument(
            "--list-files",
            dest="list_files",
            default=False,
            action="store_true",
            help="Dont generate files, but instead just list the files that will be \
                generated, and external files that need to be included.",
        )

        arg_group.add_argument(
            "--skip-buses",
            dest="skip_buses",
            default=False,
            action="store_true",
            help="Addrmaps containing only addrmaps, not registers, can be removed by \
                passing --skip-buses flag.",
        )

        arg_group.add_argument(
            "--generate-tests",
            dest="generate_tests",
            default=False,
            action="store_true",
            help="Generate tests",
        )

    def do_export(self, top_node: AddrmapNode, options: argparse.Namespace) -> None:
        """Invoked by PeakRDL to run the export after argument parsing.

        Parameters
        ----------
        top_node : AddrmapNode
            Top-level addrmap node from the compiled SystemRDL input.
        options : argparse.Namespace
            Parsed CLI arguments, including ``output``, ``list_files``,
            ``ext``, ``skip_buses``, and ``generate_tests``.
        """
        hal = HalExporter()
        hal.export(
            node=top_node,
            outdir=options.output,
            list_files=options.list_files,
            ext_modules=options.ext,
            skip_buses=options.skip_buses,
        )

        if options.generate_tests:
            tests = TestGenerator()

            test_outdir = pathlib.Path(options.output) / "tests"
            test_outdir.mkdir(parents=True, exist_ok=True)
            tests.export(node=top_node, outdir=str(test_outdir))
