# tikz-mcp

A lightweight MCP (Model Context Protocol) server that compiles TikZ code into high-resolution PNG images. Lets AI assistants render and preview LaTeX/TikZ diagrams during conversations.

## Features

- **Single tool**: `compile_tikz` -- pass TikZ code, get a PNG image
- **Auto-wrapping**: Raw TikZ commands are automatically wrapped in a `standalone` document
- **Custom preamble**: Pass your own `\usepackage` / `\usetikzlibrary` commands
- **High resolution**: Output at 1000 DPI by default
- **Graceful errors**: LaTeX compilation errors are captured and returned as readable messages
- **Zero idle cost**: Uses stdio transport -- no background process when not in use

## Prerequisites

- **Python** >= 3.10
- **LaTeX**: `pdflatex` in PATH (e.g. via [MacTeX](https://www.tug.org/mactex/) or TeX Live)
- **Poppler**: `pdftoppm` in PATH (install via `brew install poppler`)

## Installation

```bash
pip install tikz-mcp
```

Or install from source:

```bash
git clone https://github.com/FlorianHuo/tikz-mcp.git
cd tikz-mcp
pip install .
```

## Usage

### As an MCP server (stdio)

Add to your MCP client config (e.g. Antigravity `settings.json`, Claude Desktop `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "tikz-mcp": {
      "command": "tikz-mcp",
      "args": []
    }
  }
}
```

Or run with python:

```json
{
  "mcpServers": {
    "tikz-mcp": {
      "command": "python3",
      "args": ["-m", "tikz_mcp.server"]
    }
  }
}
```

### Tool: `compile_tikz`

| Parameter   | Type   | Required | Description |
|-------------|--------|----------|-------------|
| `tikz_code` | string | Yes      | TikZ code (raw commands or full document) |
| `preamble`  | string | No       | Custom LaTeX preamble (replaces default) |

**Example -- raw TikZ code:**

```
\begin{tikzpicture}
  \draw[thick, ->] (0,0) -- (3,0) node[right] {$x$};
  \draw[thick, ->] (0,0) -- (0,3) node[above] {$y$};
  \draw[blue, thick] (0,0) circle (2);
\end{tikzpicture}
```

The server auto-wraps this in a `standalone` document with common TikZ libraries loaded.

**Example -- full document:**

```latex
\documentclass[border=5pt]{standalone}
\usepackage{tikz}
\begin{document}
\begin{tikzpicture}
  \fill[red] (0,0) rectangle (2,2);
\end{tikzpicture}
\end{document}
```

### Output

Rendered PNGs are saved to `$HOME/.tikz-mcp/output/` and the full path is returned.

## Default Preamble

When raw TikZ code is provided (without `\documentclass`), the following preamble is used:

```latex
\usepackage{tikz}
\usepackage{amsmath,amssymb}
\usetikzlibrary{
    arrows.meta, calc, decorations.pathmorphing,
    decorations.markings, patterns, positioning,
    shapes.geometric, shapes.misc, fit, backgrounds,
    intersections, through, matrix, trees,
}
```

Override by passing a custom `preamble` parameter.

## License

MIT

## Changelog

### v0.1.0

- Initial release
- `compile_tikz` tool with auto-wrapping, custom preamble, 1000 DPI output
- stdio transport for zero idle resource usage
