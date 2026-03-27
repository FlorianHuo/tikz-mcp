"""
TikZ MCP Server - Compile and preview TikZ diagrams via MCP.

A lightweight MCP server that lets AI assistants compile TikZ code
into high-resolution PNG images during conversations.
"""

import asyncio
import os
import shutil
import tempfile
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Directory containing this file (used to locate STYLE_GUIDE.md)
_PKG_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _PKG_DIR.parent.parent


def _load_style_guide() -> str:
    """Load the style guide from STYLE_GUIDE.md bundled with the project."""
    style_path = _PROJECT_DIR / "STYLE_GUIDE.md"
    if style_path.exists():
        return style_path.read_text(encoding="utf-8")
    return ""

# Default preamble for standalone TikZ documents
DEFAULT_PREAMBLE = r"""\usepackage{tikz}
\usepackage{amsmath,amssymb}
\usetikzlibrary{
    arrows.meta,
    calc,
    decorations.pathmorphing,
    decorations.markings,
    patterns,
    positioning,
    shapes.geometric,
    shapes.misc,
    fit,
    backgrounds,
    intersections,
    through,
    matrix,
    trees,
}"""

# Output DPI for PNG rendering
OUTPUT_DPI = 1000

_STYLE_GUIDE = _load_style_guide()

_INSTRUCTIONS = (
    "This server compiles TikZ code into high-resolution PNG images. "
    "Use the compile_tikz tool to render TikZ diagrams. "
    "You can pass raw TikZ commands (they will be auto-wrapped in a "
    "standalone document) or a full LaTeX document.\n\n"
    "IMPORTANT: You MUST follow the style guide below when writing TikZ code.\n\n"
    "# Self-Verification Workflow\n\n"
    "After EVERY call to compile_tikz, you MUST:\n"
    "1. View the generated PNG image to inspect the output.\n"
    "2. Check for: label overlaps, disproportionate aspect ratios, "
    "curves that violate physical/mathematical laws, elements crowded "
    "into a narrow band, and any deviation from the style guide.\n"
    "3. If ANY issue is found, fix the TikZ code and recompile. "
    "Repeat until the output is correct.\n"
    "4. Only present the final verified image to the user.\n\n"
    + _STYLE_GUIDE
)

mcp = FastMCP(
    name="tikz-mcp",
    instructions=_INSTRUCTIONS,
)


def _is_full_document(code: str) -> bool:
    """Check if the code is a full LaTeX document or raw TikZ commands."""
    return r"\documentclass" in code


def _wrap_tikz(tikz_code: str, preamble: str) -> str:
    """Wrap raw TikZ code in a standalone LaTeX document."""
    return (
        r"\documentclass[border=8pt]{standalone}"
        "\n"
        f"{preamble}\n"
        r"\begin{document}"
        "\n"
        f"{tikz_code}\n"
        r"\end{document}"
        "\n"
    )


async def _run_process(cmd: list[str], cwd: str, timeout: int = 30) -> tuple[int, str]:
    """Run a subprocess asynchronously and return (returncode, combined output)."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    try:
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        return -1, f"Process timed out after {timeout}s"
    return proc.returncode, stdout.decode(errors="replace")


@mcp.tool()
async def compile_tikz(
    tikz_code: str,
    preamble: str = "",
) -> str:
    """Compile TikZ code into a high-resolution PNG image.

    Args:
        tikz_code: TikZ code to compile. Can be either:
            - Raw TikZ commands (will be auto-wrapped in a standalone document)
            - A full LaTeX document (if it contains \\documentclass)
        preamble: Optional custom LaTeX preamble. Only used when tikz_code is
            raw TikZ commands (not a full document). Replaces the default
            preamble which loads tikz, amsmath, amssymb and common TikZ
            libraries. Pass additional \\usepackage or \\usetikzlibrary
            commands here if needed.

    Returns:
        Absolute path to the rendered PNG image, or an error message
        if compilation fails.
    """
    # Validate input
    tikz_code = tikz_code.strip()
    if not tikz_code:
        return "Error: Empty TikZ code provided."

    # Create a persistent output directory for rendered images
    output_dir = Path.home() / ".tikz-mcp" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create a temporary working directory for compilation
    tmpdir = tempfile.mkdtemp(prefix="tikz_mcp_")
    try:
        # Prepare the LaTeX source
        if _is_full_document(tikz_code):
            latex_source = tikz_code
        else:
            effective_preamble = preamble.strip() if preamble.strip() else DEFAULT_PREAMBLE
            latex_source = _wrap_tikz(tikz_code, effective_preamble)

        # Write .tex file
        tex_path = os.path.join(tmpdir, "tikz_input.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_source)

        # Compile with pdflatex (two passes for cross-references)
        compile_cmd = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "tikz_input.tex",
        ]
        returncode, output = await _run_process(compile_cmd, cwd=tmpdir)
        if returncode != 0:
            # Extract the most useful part of the error
            error_lines = []
            capture = False
            for line in output.splitlines():
                if line.startswith("!"):
                    capture = True
                if capture:
                    error_lines.append(line)
                    if len(error_lines) >= 10:
                        break
            error_msg = "\n".join(error_lines) if error_lines else output[-2000:]
            return f"LaTeX compilation failed:\n{error_msg}"

        # Check that PDF was generated
        pdf_path = os.path.join(tmpdir, "tikz_input.pdf")
        if not os.path.exists(pdf_path):
            return "Error: PDF was not generated despite successful compilation."

        # Convert PDF to PNG with transparent background using Ghostscript
        # -sDEVICE=pngalpha: PNG output with alpha channel (transparent bg)
        # -r: resolution in DPI, -dBATCH -dNOPAUSE: non-interactive mode
        tmp_png_path = os.path.join(tmpdir, "tikz_output.png")
        convert_cmd = [
            "gs",
            "-dNOPAUSE",
            "-dBATCH",
            "-dSAFER",
            "-sDEVICE=pngalpha",
            f"-r{OUTPUT_DPI}",
            f"-sOutputFile={tmp_png_path}",
            pdf_path,
        ]
        returncode, output = await _run_process(convert_cmd, cwd=tmpdir)
        if returncode != 0:
            return f"PDF to PNG conversion failed:\n{output}"

        if not os.path.exists(tmp_png_path):
            return "Error: PNG was not generated from PDF."

        # Move to persistent output directory with a unique name
        import hashlib
        import time
        # Generate a short hash from the tikz code for easy identification
        code_hash = hashlib.md5(tikz_code.encode()).hexdigest()[:8]
        timestamp = int(time.time())
        final_name = f"tikz_{timestamp}_{code_hash}.png"
        final_path = output_dir / final_name
        shutil.move(tmp_png_path, str(final_path))

        return str(final_path)
    finally:
        # Clean up temporary directory
        shutil.rmtree(tmpdir, ignore_errors=True)


def main():
    """Entry point for the TikZ MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
