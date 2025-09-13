from pathlib import Path
import shutil
import jinja2 as jj
import os
from typing import Any, Dict, Optional
from systemrdl.node import AddrmapNode, FieldNode
from systemrdl.walker import RDLListener, RDLWalker, WalkerAction


class FieldListener(RDLListener):

    def __init__(self) -> None:
        self.fields: list[FieldNode] = []
        self.curr_addrmap: AddrmapNode|None = None

    def enter_Field(self, node: FieldNode) -> Optional[WalkerAction]:
        self.fields.append(node)

    def enter_Addrmap(self, node: AddrmapNode) -> Optional[WalkerAction]:
        if self.curr_addrmap is None:
            self.curr_addrmap = node
        else:
            return WalkerAction.SkipDescendants

class TestGeneratorListener(RDLListener):

    def __init__(self) -> None:
        self.addrmaps: list[AddrmapNode] = []

    def enter_Addrmap(self, node: AddrmapNode) -> Optional[WalkerAction]:
        self.addrmaps.append(node)
    

class TestGenerator:

    def __init__(self) -> None:
        pass

    def export(self,
               node: AddrmapNode,
               outdir: str) -> None:

        walker = RDLWalker(unroll=True)
        listener = TestGeneratorListener()
        walker.walk(node, listener)


        for addrmap in listener.addrmaps:
            field_listener = FieldListener()
            walker.walk(addrmap, field_listener)

            context: dict[str, Any] = {
                    "top": node,
                    "fields": field_listener.fields,
                    }
            test_content: str = self.process_template(context, "test.cpp.j2")

            out_file = os.path.join(
                outdir, f"test_{addrmap.get_path('_')}.cpp")

            with open(out_file, "w") as f:
                f.write(test_content)

        cmake_context: dict[str, Any] = {
                "addrmaps": listener.addrmaps,
                }
        cmake_content: str = self.process_template(cmake_context, "test_CMakeLists.txt.j2")
        cmake_out_file = os.path.join(
            outdir, "CMakeLists.txt")

        with open(cmake_out_file, "w") as f:
            f.write(cmake_content)


        self.copy_test_directory(outdir)



    def process_template(self, 
                         context: Dict,
                         template: str,
                         ) -> str:
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
        cpp_header_text = env.get_template(template).render(context)
        return cpp_header_text

    def copy_test_directory(self, outdir: str):
        curr_dir: Path = Path(__file__).resolve().parent
        src: Path = curr_dir / "test_generator" 
        dst = Path(outdir)

        shutil.copytree(src, dst, dirs_exist_ok=True)

