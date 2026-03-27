# TikZ Diagram Style Guide

This document defines the aesthetic rules for all TikZ diagrams produced via tikz-mcp. AI assistants MUST follow these rules when generating TikZ code.

## 1. Color

- **Monochrome first**: Default to black/dark gray for all lines and text. Use color only when it serves a functional purpose (e.g., distinguishing overlapping curves that cannot be separated by line style alone).
- **Accent palette**: When color is necessary, use at most **2--3 muted tones** from a single hue family (e.g., `black`, `gray!60`, one accent). Avoid saturated primaries (pure red, blue, green).
- **No rainbow**: Never assign a different color to every element. Group related elements under the same visual treatment.
- **Fill**: Use light fills sparingly (`gray!8` or `gray!12`) for enclosed regions. Never use opaque or vivid fills.

## 2. Layout and Spacing

- **No overlaps**: Labels, arrows, curves, and nodes must never overlap or cross each other. Adjust label placement (`above`, `below`, `left`, `right`, `anchor`, `xshift`, `yshift`) until every element has clear space.
- **Uniform margins**: Maintain consistent spacing between parallel elements (axis ticks, labels, curves). Axis labels should sit at a uniform distance from the axis line.
- **Balanced composition**: The diagram should feel centered and symmetrical where appropriate. Avoid large empty regions on one side while the other side is crowded.
- **Label placement**: Prefer placing labels at curve endpoints or in open whitespace areas. Use `pos=` along paths to fine-tune. Use leader lines or callouts if inline placement would cause clutter.

## 3. Typography

- **Font size**: Use `\small` or `\footnotesize` for labels. Use `\normalsize` for titles only. Never use `\large` or `\Large` inside the diagram body.
- **Math mode**: All variables and formulas must be in math mode (`$...$`). Units and descriptive text stay in text mode.
- **Consistency**: All labels of the same category (e.g., axis labels, state labels, annotations) must use the same font size and weight.

## 4. Lines and Curves

- **Line weight hierarchy**: Use `thick` (0.8pt) for primary curves, `semithick` (0.6pt) for axes, `thin` (0.4pt) for grid lines or helpers. Never use `very thick` or `ultra thick`.
- **Line style for distinction**: When multiple curves share the same plot area, distinguish them by dash pattern (`dashed`, `dotted`, `dash dot`) before resorting to color.
- **Arrows**: Use `->` or `-Stealth` style. Arrow tips should be proportional to line weight. Avoid oversized arrowheads.
- **Smooth curves**: Use `smooth` or Bezier controls for curves. Avoid jagged polylines for continuous functions.

## 5. Axes and Grids

- **Axis style**: Axes use `semithick`, `->` arrows. Label the axis variable at the tip (e.g., `node[right] {$V$}`).
- **Tick marks**: Short, consistent tick marks (`2pt` length). Tick labels placed outside the plot area.
- **Grid**: Only add grid lines if the diagram demands quantitative reading. Use `very thin, gray!30` for grids.
- **Origin**: Mark the origin with `$O$` or `$0$` only when it is meaningful.

## 6. Annotations

- **Arrow annotations**: Use `thin, gray!60, ->` for annotation leader lines. Do not let annotation arrows cross data curves.
- **Braces**: Use `decorate, decoration={brace, amplitude=4pt}` for range indicators. Keep brace amplitude small.
- **Shading/hatching**: Use `pattern=north east lines, pattern color=gray!40` for regions, not solid fills.

## 7. Overall Composition

- **`standalone` border**: Use `border=8pt` to give the diagram breathing room.
- **Aspect ratio**: Prefer roughly 4:3 or 1:1 aspect ratios. Avoid extremely wide or tall diagrams.
- **Scale**: Set `scale` so that the rendered PNG is readable at normal viewing size. Typical: `scale=1.0` to `scale=1.5`.
- **Simplicity**: Every visual element must serve a purpose. Remove decorative flourishes, unnecessary gridlines, and redundant labels.
