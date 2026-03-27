# TikZ MCP Server

## Background

I need a lightweight MCP server that lets AI assistants compile and preview TikZ diagrams during conversations. Currently, when AI writes TikZ code, I can't see the result, so errors go unnoticed and the output is often wrong.

## Requirements

### Core
- A single MCP tool: `compile_tikz`
  - Input: TikZ code (string)
  - Process: write to temp `.tex` file, compile with `pdflatex`, convert to PNG
  - Output: path to the rendered PNG image
- **stdio transport** (not HTTP) -- zero resource usage when idle, only runs when invoked

### Constraints
- Lightweight: minimal dependencies, no Docker, no heavy frameworks
- Use the system's existing LaTeX installation (XeLaTeX/pdflatex already installed)
- Python implementation preferred (simple, easy to maintain)
- Should handle compilation errors gracefully and return the error message
- Clean up temp files after compilation
- PNG output should be high resolution (dpi=1000 per my preferences)

### Nice to have
- Support for standalone document class (auto-wrap raw TikZ code in a compilable document)
- Option to pass custom preamble (for loading specific TikZ libraries)

## Technical Notes
- MCP server spec: https://modelcontextprotocol.io
- Python MCP SDK: `mcp` package on PyPI
- Image conversion: `pdftoppm` (from poppler) or `sips` (built-in macOS)
- LaTeX is installed via MacTeX, `pdflatex` is in PATH

## Reference
- This project originated from `reflections/tracks/trivial.md` item: "tikz 作图美化 MCP"
