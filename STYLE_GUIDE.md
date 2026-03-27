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
- **Uniform style within a path**: All segments of a single closed path (e.g., a thermodynamic cycle, a circuit loop) MUST use the same line style. Never mix solid and dashed within one closed loop. Dash patterns are for distinguishing **different curve families overlaid on the same axes** (e.g., two functions on one plot), not segments of one path.
- **Arrows**: Use `->` or `-Stealth` style. Arrow tips should be proportional to line weight. Avoid oversized arrowheads.
- **Mathematical curves**: When a curve follows a known equation, ALWAYS use `plot[domain=..., samples=50]` with the real function. Never approximate known functions with Bezier curves.

Correct -- real hyperbola:
```latex
\draw[thick] plot[domain=1.2:3.0, samples=50] (\x, {3.6/\x});
```

Wrong -- Bezier approximation of a hyperbola:
```latex
% DO NOT do this when the equation is known
\draw[thick] (1.2,3.0) .. controls (1.8,2.0) and (2.5,1.4) .. (3.0,1.2);
```

Use Bezier curves only for curves without a closed-form equation (e.g., schematic adiabats where the exponent creates `Dimension too large` errors in pgfmath).

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
- **Coordinate range check**: Before drawing, verify that all coordinates fit within reasonable TikZ dimensions (generally keep values below 15 to avoid `Dimension too large` errors). If using `scale`, remember that `scale * max_coordinate` is the actual dimension.

## 8. Physical and Mathematical Accuracy

- **Domain knowledge**: When drawing diagrams from physics, chemistry, or mathematics, the curves MUST reflect the correct qualitative behavior. For example:
  - Isotherms on P-V diagrams are hyperbolas (P = C/V), not straight lines
  - Adiabats are steeper than isotherms
  - Supply/demand curves have correct slope signs
  - Exponential growth is convex, logistic growth has an inflection point
- **Verify state points**: Before drawing, compute key coordinate values from the governing equations and verify they are consistent (e.g., check that P*V = const for all points claimed to be on the same isotherm).
- **Use `plot` with real functions** whenever the mathematical form is known:

```latex
% Isotherm: P = C/V
\draw[thick] plot[domain=1:5, samples=50] (\x, {4.5/\x});

% Gaussian
\draw[thick] plot[domain=-3:3, samples=80] (\x, {exp(-\x*\x/2)});

% Parabola
\draw[thick] plot[domain=-2:2, samples=50] (\x, {\x*\x});
```

## 9. TikZ Technical Pitfalls

- **`Dimension too large`**: Avoid coordinates or intermediate computations exceeding roughly 16000pt (about 560cm). Common causes:
  - `exp()` with large arguments -- clamp domains to avoid overflow
  - `1/\x` near zero -- set domain minimum well above 0
  - Large `scale` factors multiplied by large coordinates
  - Using `pow(\x, n)` with non-integer n inside `\clip` paths (use sampled polygon instead)
- **Hatched fill with complex paths**: When filling regions bounded by `plot` curves, do NOT use `\clip` + `plot` (causes dimension overflow). Instead, sample the curve coordinates into a polygon:

```latex
% Correct: sampled polygon for hatched fill
\fill[pattern=north east lines, pattern color=gray!35]
    (1.2,3.0) -- (1.6,2.25) -- (2.0,1.8) -- (2.4,1.5) -- (3.0,1.2)
    .. controls (3.6,0.68) and (4.4,0.38) .. (5.0,0.32)
    -- (4.2,0.381) -- (3.0,0.533) -- (2.0,0.8)
    .. controls (1.7,1.5) and (1.3,2.4) .. (1.2,3.0)
    -- cycle;
```

- **Decreasing `plot` domains**: `plot[domain=5:2]` may not work reliably in all TikZ versions. To draw a curve from right to left (e.g., for correct arrow direction), draw the path left-to-right and use `\arrowreversed` via the `markings` decoration:

```latex
\tikzset{
    rarr/.style={decoration={markings, mark=at position 0.55 with
        {\arrowreversed{Stealth[length=5pt]}}}, postaction={decorate}}
}
\draw[thick, rarr] plot[domain=2:5, samples=50] (\x, {1.6/\x});
```
