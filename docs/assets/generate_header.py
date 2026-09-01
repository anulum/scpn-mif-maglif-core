# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — repository header artwork generator

"""Generate the three README header images (1280x640) for this repository.

Every image is original generated artwork derived from this repository's
own domain surface — the three-stage drive whose first two stages are
hard class invariants, the magnetised liner cross-section, and the
liner aspect-ratio design window. The right-hand text panel states only
facts backed by the repository itself.

Outputs (written next to this script):

- ``repo_header.png`` — premagnetisation, laser preheat and liner
  implosion as a sequence (used by ``README.md``).
- ``repo_header_liner_section.png`` — the end view of magnetised fuel
  inside the metal liner under its drive current.
- ``repo_header_aspect_window.png`` — the aspect-ratio design window
  with flagged geometries on either side.

Generation-time tooling only: requires ``numpy`` and ``matplotlib``,
which are deliberately not part of the pinned development lock. Run as
``python3 docs/assets/generate_header.py`` from the repository root.
The output is deterministic (fixed geometry, no random input).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

OUT_DIR = Path(__file__).resolve().parent

BG = "#00050a"
CYAN = "#00ccff"
MAGENTA = "#ff00ff"
STEEL = "#334466"
PROBE = "#66aaff"
RED = "#ff3366"
GREEN = "#3ddc84"
GOLD = "#ffcc55"

WIDTH_IN, HEIGHT_IN, DPI = 12.8, 6.4, 100

TITLE_METRICS: list[tuple[str, str]] = [
    ("Device Configuration", "maglif · magnetised cylindrical liner"),
    ("Hard Invariants", "premagnetisation + laser preheat"),
    ("Reference", "Slutz et al., PoP 17 (2010) 056303"),
    ("Aspect Ratio", "outside design window flagged"),
    ("Plan Envelope", "v1.1.0 · synthetic · review-only"),
    ("Quality Gates", "100% branch cov · mypy --strict"),
]


def _pyplot() -> Any:
    """Return pyplot configured for headless Agg rendering."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _glow_cmap() -> Any:
    """Build the family glow colormap (deep navy to cyan)."""
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "scpn_glow",
        ["#00050a", "#001428", "#002d55", "#005588", "#0088bb", "#00ccff"],
    )


def _text_panel(fig: Any, subtitle: str) -> None:
    """Draw the family right-hand text panel onto ``fig``."""
    ax = fig.add_axes([0.62, 0.0, 0.38, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.08,
        0.84,
        "SCPN",
        color="white",
        fontsize=36,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.745,
        "MIF MAGLIF",
        color="white",
        fontsize=26,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.695,
        "CORE",
        color="white",
        fontsize=26,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.635,
        subtitle,
        color=CYAN,
        fontsize=11,
        fontfamily="monospace",
        alpha=0.85,
    )
    ax.plot([0.08, 0.85], [0.595, 0.595], color=STEEL, lw=0.8, alpha=0.5)
    y = 0.535
    for label, value in TITLE_METRICS:
        ax.text(
            0.08,
            y,
            f"▸ {label}",
            color="#6688aa",
            fontsize=9,
            fontfamily="monospace",
            alpha=0.9,
        )
        ax.text(
            0.10,
            y - 0.030,
            value,
            color="#99bbdd",
            fontsize=8,
            fontfamily="monospace",
            alpha=0.7,
        )
        y -= 0.072
    ax.text(
        0.08,
        0.06,
        "© 1996–2026 Miroslav Šotek",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.6,
    )
    ax.text(
        0.08,
        0.03,
        "anulum.li | AGPL-3.0",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.5,
    )


def _art_axes(fig: Any) -> Any:
    """Return the borderless left-hand art axes of ``fig``."""
    ax = fig.add_axes([0.0, 0.0, 0.68, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def _save(fig: Any, plt: Any, name: str) -> None:
    """Save ``fig`` to ``name`` inside the assets directory and close it."""
    target = OUT_DIR / name
    fig.savefig(target, dpi=DPI, facecolor=BG, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print(f"generated {target}")


def _fuel_glow(
    ax: Any,
    centre_x: float,
    half_width: float,
    y_bottom: float,
    y_top: float,
    gain: float = 1.0,
) -> None:
    """Draw the glowing fuel column of one drive stage."""
    grid_x = np.linspace(centre_x - 3.0 * half_width, centre_x + 3.0 * half_width, 140)
    grid_y = np.linspace(y_bottom, y_top, 160)
    mesh_x, mesh_y = np.meshgrid(grid_x, grid_y)
    rho = np.abs(mesh_x - centre_x) / half_width
    ax.contourf(
        mesh_x,
        mesh_y,
        np.exp(-rho * 1.9) * gain,
        levels=26,
        cmap=_glow_cmap(),
        alpha=0.9,
    )


def _liner_walls(
    ax: Any,
    centre_x: float,
    inner: float,
    thickness: float,
    y_bottom: float,
    y_top: float,
) -> None:
    """Draw the metal liner walls of one drive stage."""
    for sign in (-1, +1):
        x_inner = centre_x + sign * inner
        x_outer = centre_x + sign * (inner + thickness)
        for wall_x in (x_inner, x_outer):
            ax.plot(
                [wall_x, wall_x],
                [y_bottom, y_top],
                color=STEEL,
                lw=2.4,
                alpha=0.9,
            )
        ax.fill_betweenx(
            [y_bottom, y_top],
            x_inner,
            x_outer,
            color="#22303f",
            alpha=0.75,
        )


def generate_drive_stages() -> None:
    """Generate ``repo_header.png``: the three defining drive stages."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-3.2, 3.2)

    stages = [
        (1.75, "premagnetise", "axial B_z frozen into the fuel", 0.62, 0.30),
        (5.0, "laser preheat", "axial entrance-hole beam", 0.62, 0.55),
        (8.05, "liner implosion", "current-driven compression", 0.30, 1.0),
    ]
    for centre_x, title, subtitle, half_width, gain in stages:
        _fuel_glow(ax, centre_x, half_width, -1.55, 1.55, gain=gain)
        _liner_walls(ax, centre_x, half_width + 0.14, 0.16, -1.55, 1.55)
        ax.text(
            centre_x,
            -2.05,
            title,
            color="#99bbdd",
            fontsize=8.5,
            fontfamily="monospace",
            ha="center",
            alpha=0.95,
        )
        ax.text(
            centre_x,
            -2.4,
            subtitle,
            color="#445566",
            fontsize=7.5,
            fontfamily="monospace",
            ha="center",
        )

        if title == "premagnetise":
            for base_y in (-1.15, -0.4, 0.35, 1.1):
                ax.annotate(
                    "",
                    xy=(centre_x, base_y + 0.55),
                    xytext=(centre_x, base_y),
                    arrowprops={
                        "arrowstyle": "->",
                        "color": MAGENTA,
                        "lw": 1.5,
                        "alpha": 0.9,
                    },
                )
            ax.text(
                centre_x + 0.78,
                0.0,
                "B_z",
                color=MAGENTA,
                fontsize=9,
                fontfamily="monospace",
                alpha=0.95,
            )
        if title == "laser preheat":
            ax.annotate(
                "",
                xy=(centre_x, 0.55),
                xytext=(centre_x, 2.35),
                arrowprops={
                    "arrowstyle": "-|>",
                    "color": GOLD,
                    "lw": 2.4,
                    "alpha": 0.95,
                    "mutation_scale": 13,
                },
            )
            ax.text(
                centre_x + 0.24,
                1.95,
                "laser",
                color=GOLD,
                fontsize=8.5,
                fontfamily="monospace",
                alpha=0.95,
            )
            for base_y in (-1.15, -0.4, 0.35, 1.1):
                ax.annotate(
                    "",
                    xy=(centre_x, base_y + 0.4),
                    xytext=(centre_x, base_y),
                    arrowprops={
                        "arrowstyle": "->",
                        "color": MAGENTA,
                        "lw": 1.0,
                        "alpha": 0.45,
                    },
                )
        if title == "liner implosion":
            for base_y in (-1.05, -0.35, 0.35, 1.05):
                for sign in (-1, +1):
                    ax.annotate(
                        "",
                        xy=(centre_x + sign * 0.52, base_y),
                        xytext=(centre_x + sign * 1.15, base_y),
                        arrowprops={
                            "arrowstyle": "->",
                            "color": PROBE,
                            "lw": 1.3,
                            "alpha": 0.85,
                        },
                    )
            ax.text(
                centre_x,
                1.95,
                r"$J \times B$ on the liner",
                color=PROBE,
                fontsize=8,
                fontfamily="monospace",
                ha="center",
                alpha=0.95,
            )

    ax.annotate(
        "",
        xy=(6.55, 2.75),
        xytext=(3.45, 2.75),
        arrowprops={"arrowstyle": "->", "color": STEEL, "lw": 1.2, "alpha": 0.7},
    )
    ax.text(
        5.0,
        2.95,
        "time",
        color="#667799",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    ax.text(
        5.0,
        -2.95,
        "premagnetisation and preheat are hard invariants of this class",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Three Stages That Define The Class")
    _save(fig, plt, "repo_header.png")


def generate_liner_section() -> None:
    """Generate ``repo_header_liner_section.png``: the end view."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(-2.9, 2.9)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")

    theta = np.linspace(0.0, 2.0 * np.pi, 300)
    grid = np.linspace(-1.2, 1.2, 180)
    mesh_x, mesh_y = np.meshgrid(grid, grid)
    rho = np.sqrt(mesh_x**2 + mesh_y**2) / 0.55
    ax.contourf(
        mesh_x,
        mesh_y,
        np.exp(-rho * 1.7),
        levels=30,
        cmap=_glow_cmap(),
        alpha=0.92,
    )

    for radius in (0.78, 0.95):
        ax.plot(
            radius * np.cos(theta),
            radius * np.sin(theta),
            color=STEEL,
            lw=2.4,
            alpha=0.95,
        )
    ax.text(
        1.12,
        0.72,
        "metal liner",
        color="#8899aa",
        fontsize=8.5,
        fontfamily="monospace",
        alpha=0.9,
    )

    for radius, count in ((0.0, 1), (0.24, 6), (0.46, 10)):
        for index in range(count):
            angle = 2.0 * np.pi * index / max(count, 1)
            ax.plot(
                radius * np.cos(angle),
                radius * np.sin(angle),
                "o",
                color=MAGENTA,
                ms=4,
                alpha=0.9,
            )
    ax.text(
        -1.95,
        0.95,
        "B_z out of plane · premagnetised fuel",
        color=MAGENTA,
        fontsize=8,
        fontfamily="monospace",
        alpha=0.95,
    )

    for index in range(10):
        angle = 2.0 * np.pi * index / 10
        base_x, base_y = 1.12 * np.cos(angle), 1.12 * np.sin(angle)
        delta_x, delta_y = -np.sin(angle) * 0.13, np.cos(angle) * 0.13
        ax.annotate(
            "",
            xy=(base_x + delta_x, base_y + delta_y),
            xytext=(base_x - delta_x, base_y - delta_y),
            arrowprops={"arrowstyle": "->", "color": PROBE, "lw": 1.2, "alpha": 0.8},
        )
    ax.text(
        1.32,
        -0.85,
        "drive current",
        color=PROBE,
        fontsize=8,
        fontfamily="monospace",
        alpha=0.9,
    )

    for index in range(8):
        angle = 2.0 * np.pi * index / 8 + np.pi / 8
        outer = (1.02 * np.cos(angle), 1.02 * np.sin(angle))
        inner = (0.66 * np.cos(angle), 0.66 * np.sin(angle))
        ax.annotate(
            "",
            xy=inner,
            xytext=outer,
            arrowprops={"arrowstyle": "->", "color": "white", "lw": 1.0, "alpha": 0.55},
        )

    ax.text(
        0,
        -1.32,
        "the field is compressed with the fuel · magnetised inertial fusion",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Field And Fuel, Compressed Together")
    _save(fig, plt, "repo_header_liner_section.png")


def generate_aspect_window() -> None:
    """Generate ``repo_header_aspect_window.png``: the geometry gate."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    ax.plot([1.0, 9.2], [1.7, 1.7], color=STEEL, lw=1.0, alpha=0.7)
    ax.plot([1.0, 1.0], [1.7, 9.1], color=STEEL, lw=1.0, alpha=0.7)
    ax.text(
        8.85,
        1.25,
        "liner wall thickness",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
        ha="right",
    )
    ax.text(
        1.32,
        8.85,
        "aspect ratio  R / Δ",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
    )

    thickness = np.linspace(0.10, 1.0, 300)
    px = 1.0 + 8.0 * thickness
    py = 1.7 + 0.62 * np.clip(1.0 / thickness, 0, 12)
    ax.plot(px, py, color=CYAN, lw=2.6, alpha=0.95)

    y_low = 1.7 + 0.62 * 4.0
    y_high = 1.7 + 0.62 * 9.0
    ax.fill_between([1.0, 9.0], y_low, y_high, color=GREEN, alpha=0.08)
    for level in (y_low, y_high):
        ax.plot(
            [1.0, 9.0],
            [level, level],
            color=GREEN,
            lw=1.0,
            alpha=0.6,
            ls=(0, (5, 3)),
        )
    ax.text(
        6.4,
        (y_low + y_high) / 2,
        "documented design window",
        color=GREEN,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        va="center",
        alpha=0.95,
    )

    for wall, inside in ((0.105, False), (0.16, True), (0.34, False)):
        mark_x = 1.0 + 8.0 * wall
        mark_y = 1.7 + 0.62 * min(1.0 / wall, 12)
        if inside:
            ax.plot(mark_x, mark_y, "o", color=CYAN, ms=7, alpha=0.95)
        else:
            ax.plot(
                mark_x,
                mark_y,
                "x",
                color=RED,
                ms=9,
                mew=2.2,
                alpha=0.95,
            )
    ax.text(
        2.45,
        8.35,
        "too thin · aspect ratio above window",
        color=RED,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        4.55,
        2.45,
        "too thick · aspect ratio below window",
        color=RED,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    ax.text(
        5.0,
        0.75,
        "declared liner geometry checked against the documented window",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "A Liner Inside Its Window")
    _save(fig, plt, "repo_header_aspect_window.png")


if __name__ == "__main__":
    generate_drive_stages()
    generate_liner_section()
    generate_aspect_window()
