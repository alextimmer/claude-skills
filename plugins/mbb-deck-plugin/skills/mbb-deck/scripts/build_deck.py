#!/usr/bin/env python3
"""
build_deck.py — Convert an MBB-style storyline JSON into a styled .pptx file.

Usage:
    python build_deck.py <storyline.json> [--out output.pptx] [--palette navy|red|green|neutral]

The storyline JSON schema is documented in assets/storyline_schema.json.
A worked example lives in examples/sample-storyline.json.

This script applies the visual rules in references/visual-style.md mechanically
so they don't drift from one slide to the next.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

# --------------------------------------------------------------------------
# Configuration loaders
# --------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
ASSETS_DIR = SKILL_ROOT / "assets"


def load_palettes() -> dict:
    return json.loads((ASSETS_DIR / "palettes.json").read_text())


def load_style() -> dict:
    return json.loads((ASSETS_DIR / "style_config.json").read_text())


def hex_to_rgb(hex_str: str) -> RGBColor:
    h = hex_str.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# --------------------------------------------------------------------------
# Builder
# --------------------------------------------------------------------------


class DeckBuilder:
    def __init__(self, storyline: dict, palette_name: str | None = None):
        self.story = storyline
        meta = storyline.get("meta", {})
        palettes = load_palettes()
        chosen = palette_name or meta.get("palette") or palettes["default_palette"]
        if chosen not in palettes["palettes"]:
            raise ValueError(
                f"Unknown palette: {chosen}. Choose from {list(palettes['palettes'])}"
            )
        self.palette = palettes["palettes"][chosen]
        self.style = load_style()

        self.prs = Presentation()
        self.prs.slide_width = Inches(self.style["slide"]["width_in"])
        self.prs.slide_height = Inches(self.style["slide"]["height_in"])

        # Counters
        self._page_num = 0
        self._total_pages = self._count_pages(storyline.get("slides", []))

    def _count_pages(self, slides: list[dict]) -> int:
        # Title slide does not count toward page numbering
        return sum(1 for s in slides if s.get("type") != "title")

    # ----- low-level helpers -----

    def _blank_slide(self):
        layout = self.prs.slide_layouts[6]  # 6 = blank in default theme
        slide = self.prs.slides.add_slide(layout)
        # White background
        bg_fill = slide.background.fill
        bg_fill.solid()
        bg_fill.fore_color.rgb = hex_to_rgb(self.palette["background"])
        return slide

    def _add_text(
        self,
        slide,
        x_in,
        y_in,
        w_in,
        h_in,
        text,
        font_size=14,
        bold=False,
        color_hex=None,
        align=PP_ALIGN.LEFT,
        anchor=MSO_ANCHOR.TOP,
        font=None,
    ):
        tb = slide.shapes.add_textbox(
            Inches(x_in), Inches(y_in), Inches(w_in), Inches(h_in)
        )
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        tf.margin_left = tf.margin_right = Emu(0)
        tf.margin_top = tf.margin_bottom = Emu(0)
        tf.text = text
        p = tf.paragraphs[0]
        p.alignment = align
        run = p.runs[0] if p.runs else p.add_run()
        run.text = text
        run.font.size = Pt(font_size)
        run.font.bold = bold
        run.font.name = font or self.style["typography"]["body_font"]
        if color_hex:
            run.font.color.rgb = hex_to_rgb(color_hex)
        return tb

    def _add_action_title(self, slide, title_text, framing_line=None):
        sp = self.style["spacing"]
        ty = self.style["typography"]
        margin = self.style["slide"]["margin_in"]
        width = self.style["slide"]["width_in"] - 2 * margin
        self._add_text(
            slide,
            x_in=margin,
            y_in=sp["title_top_in"],
            w_in=width,
            h_in=sp["title_height_in"],
            text=title_text,
            font_size=ty["action_title_pt"],
            bold=ty["action_title_bold"],
            color_hex=self.palette["accent"],
            font=ty["title_font"],
        )
        if framing_line:
            framing_y = sp["title_top_in"] + sp["title_height_in"]
            self._add_text(
                slide,
                x_in=margin,
                y_in=framing_y,
                w_in=width,
                h_in=sp["framing_line_height_in"],
                text=framing_line,
                font_size=ty["framing_line_pt"],
                color_hex=self.palette["neutral_dark"],
                font=ty["body_font"],
            )

    def _body_top(self, has_framing_line: bool) -> float:
        """Body content starts lower when a framing line is present."""
        sp = self.style["spacing"]
        if has_framing_line:
            return (
                sp["title_top_in"]
                + sp["title_height_in"]
                + sp["framing_line_height_in"]
                + 0.1
            )
        return sp["body_top_in"]

    def _add_footer(self, slide, source_text=None):
        if self._page_num <= 0:
            return
        sp = self.style["spacing"]
        ty = self.style["typography"]
        margin = self.style["slide"]["margin_in"]
        slide_w = self.style["slide"]["width_in"]
        slide_h = self.style["slide"]["height_in"]
        y = slide_h - sp["footer_height_in"] - sp["footer_y_offset_in"]

        # Source bottom-left
        if source_text:
            self._add_text(
                slide,
                margin,
                y,
                slide_w - 2 * margin - 1.0,
                sp["footer_height_in"],
                f"Source: {source_text}",
                font_size=ty["footnote_pt"],
                color_hex=self.palette["footnote"],
                align=PP_ALIGN.LEFT,
            )

        # Page number bottom-right
        self._add_text(
            slide,
            slide_w - margin - 1.0,
            y,
            1.0,
            sp["footer_height_in"],
            str(self._page_num),
            font_size=ty["footnote_pt"],
            color_hex=self.palette["footnote"],
            align=PP_ALIGN.RIGHT,
        )

        # Confidentiality (center) if specified
        meta = self.story.get("meta", {})
        confid = meta.get("confidentiality")
        if confid:
            self._add_text(
                slide,
                margin,
                y,
                slide_w - 2 * margin,
                sp["footer_height_in"],
                confid,
                font_size=ty["footnote_pt"],
                color_hex=self.palette["footnote"],
                align=PP_ALIGN.CENTER,
            )

    # ----- slide renderers -----

    def render_title(self, spec):
        slide = self._blank_slide()
        meta = self.story.get("meta", {})
        ty = self.style["typography"]
        slide_w = self.style["slide"]["width_in"]
        slide_h = self.style["slide"]["height_in"]

        # Center vertically
        title = spec.get("title") or meta.get("title", "Untitled")
        subtitle = spec.get("subtitle") or meta.get("subtitle", "")
        date = spec.get("date") or meta.get("date", "")
        prepared_for = spec.get("prepared_for") or meta.get("prepared_for", "")
        prepared_by = spec.get("prepared_by") or meta.get("prepared_by", "")

        cy = slide_h / 2 - 1.5
        self._add_text(
            slide,
            1,
            cy,
            slide_w - 2,
            1.0,
            title,
            font_size=ty["title_slide_main_pt"],
            bold=True,
            color_hex=self.palette["accent"],
            font=ty["title_font"],
        )
        if subtitle:
            self._add_text(
                slide,
                1,
                cy + 1.0,
                slide_w - 2,
                0.7,
                subtitle,
                font_size=ty["title_slide_subtitle_pt"],
                color_hex=self.palette["body_text"],
            )
        meta_y = cy + 2.2
        meta_lines = [
            m
            for m in [
                date,
                prepared_for and f"Prepared for: {prepared_for}",
                prepared_by and f"Prepared by: {prepared_by}",
            ]
            if m
        ]
        for i, line in enumerate(meta_lines):
            self._add_text(
                slide,
                1,
                meta_y + i * 0.3,
                slide_w - 2,
                0.3,
                line,
                font_size=ty["title_slide_meta_pt"],
                color_hex=self.palette["neutral_mid"],
            )

    def render_exec_summary(self, spec):
        slide = self._blank_slide()
        ty = self.style["typography"]
        margin = self.style["slide"]["margin_in"]
        slide_w = self.style["slide"]["width_in"]
        sp = self.style["spacing"]

        self._add_action_title(slide, spec["title"], spec.get("framing_line"))
        # Supporting points as numbered list with accent number markers
        points = spec.get("supporting_points", [])
        body_top = self._body_top(bool(spec.get("framing_line")))
        avail_h = self.style["slide"]["height_in"] - body_top - 1.0
        line_h = min(0.7, avail_h / max(len(points), 1))
        for i, pt in enumerate(points):
            y = body_top + i * line_h
            # Number circle
            num = self._add_text(
                slide,
                margin,
                y,
                0.5,
                line_h,
                str(i + 1),
                font_size=ty["exec_summary_point_pt"],
                bold=True,
                color_hex=self.palette["accent"],
                align=PP_ALIGN.LEFT,
                anchor=MSO_ANCHOR.MIDDLE,
            )
            self._add_text(
                slide,
                margin + 0.6,
                y,
                slide_w - 2 * margin - 0.6,
                line_h,
                pt,
                font_size=ty["exec_summary_point_pt"],
                color_hex=self.palette["body_text"],
                anchor=MSO_ANCHOR.MIDDLE,
            )
        self._add_footer(slide, spec.get("source"))

    def render_bullets(self, spec):
        slide = self._blank_slide()
        ty = self.style["typography"]
        margin = self.style["slide"]["margin_in"]
        sp = self.style["spacing"]
        slide_w = self.style["slide"]["width_in"]

        self._add_action_title(slide, spec["title"], spec.get("framing_line"))
        bullets = spec.get("bullets", [])
        body_top = self._body_top(bool(spec.get("framing_line")))
        avail_h = self.style["slide"]["height_in"] - body_top - 1.0

        tb = slide.shapes.add_textbox(
            Inches(margin),
            Inches(body_top),
            Inches(slide_w - 2 * margin),
            Inches(avail_h),
        )
        tf = tb.text_frame
        tf.word_wrap = True

        for i, bullet in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = f"•  {bullet}"
            p.alignment = PP_ALIGN.LEFT
            for run in p.runs:
                run.font.size = Pt(ty["bullet_pt"])
                run.font.color.rgb = hex_to_rgb(self.palette["body_text"])
                run.font.name = ty["body_font"]
            p.space_after = Pt(8)

        self._add_footer(slide, spec.get("source"))

    def render_two_by_two(self, spec):
        slide = self._blank_slide()
        margin = self.style["slide"]["margin_in"]
        sp = self.style["spacing"]
        slide_w = self.style["slide"]["width_in"]

        self._add_action_title(slide, spec["title"], spec.get("framing_line"))

        # Matrix area
        mx = margin + 1.2  # leave room for y-axis label
        my = self._body_top(bool(spec.get("framing_line")))
        mw = slide_w - 2 * margin - 1.5
        mh = self.style["slide"]["height_in"] - my - 1.5

        # Outer box
        outer = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(mx), Inches(my), Inches(mw), Inches(mh)
        )
        outer.fill.background()
        outer.line.color.rgb = hex_to_rgb(self.palette["neutral_mid"])
        outer.line.width = Pt(0.75)

        # Cross lines
        v = slide.shapes.add_connector(
            1, Inches(mx + mw / 2), Inches(my), Inches(mx + mw / 2), Inches(my + mh)
        )
        v.line.color.rgb = hex_to_rgb(self.palette["neutral_mid"])
        v.line.width = Pt(0.5)
        h = slide.shapes.add_connector(
            1, Inches(mx), Inches(my + mh / 2), Inches(mx + mw), Inches(my + mh / 2)
        )
        h.line.color.rgb = hex_to_rgb(self.palette["neutral_mid"])
        h.line.width = Pt(0.5)

        # Axis labels
        x_axis = spec.get("x_axis", {})
        y_axis = spec.get("y_axis", {})
        ty = self.style["typography"]

        # X axis label below
        self._add_text(
            slide,
            mx,
            my + mh + 0.25,
            mw,
            0.35,
            x_axis.get("label", ""),
            font_size=11,
            bold=True,
            color_hex=self.palette["neutral_dark"],
            align=PP_ALIGN.CENTER,
        )
        self._add_text(
            slide,
            mx,
            my + mh + 0.05,
            mw / 2,
            0.25,
            x_axis.get("low", "Low"),
            font_size=9,
            color_hex=self.palette["footnote"],
            align=PP_ALIGN.LEFT,
        )
        self._add_text(
            slide,
            mx + mw / 2,
            my + mh + 0.05,
            mw / 2,
            0.25,
            x_axis.get("high", "High"),
            font_size=9,
            color_hex=self.palette["footnote"],
            align=PP_ALIGN.RIGHT,
        )

        # Y axis label (rotated would be ideal; using horizontal stacked text)
        self._add_text(
            slide,
            margin,
            my + mh / 2 - 0.2,
            1.1,
            0.4,
            y_axis.get("label", ""),
            font_size=11,
            bold=True,
            color_hex=self.palette["neutral_dark"],
            align=PP_ALIGN.RIGHT,
        )
        self._add_text(
            slide,
            margin - 0.05,
            my + mh - 0.25,
            1.15,
            0.25,
            y_axis.get("low", "Low"),
            font_size=9,
            color_hex=self.palette["footnote"],
            align=PP_ALIGN.RIGHT,
        )
        self._add_text(
            slide,
            margin - 0.05,
            my,
            1.15,
            0.25,
            y_axis.get("high", "High"),
            font_size=9,
            color_hex=self.palette["footnote"],
            align=PP_ALIGN.RIGHT,
        )

        # Items
        for item in spec.get("items", []):
            ix = mx + item.get("x", 0.5) * mw
            iy = my + (1 - item.get("y", 0.5)) * mh  # invert y so high is up
            color = (
                self.palette["accent"]
                if item.get("highlight")
                else self.palette["neutral_mid"]
            )
            dot = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(ix - 0.1),
                Inches(iy - 0.1),
                Inches(0.2),
                Inches(0.2),
            )
            dot.fill.solid()
            dot.fill.fore_color.rgb = hex_to_rgb(color)
            dot.line.fill.background()
            self._add_text(
                slide,
                ix + 0.15,
                iy - 0.15,
                1.6,
                0.3,
                item.get("label", ""),
                font_size=10,
                bold=item.get("highlight", False),
                color_hex=color,
            )

        self._add_footer(slide, spec.get("source"))

    def render_mece_buckets(self, spec):
        slide = self._blank_slide()
        margin = self.style["slide"]["margin_in"]
        sp = self.style["spacing"]
        slide_w = self.style["slide"]["width_in"]

        self._add_action_title(slide, spec["title"], spec.get("framing_line"))

        buckets = spec.get("buckets", [])
        n = max(len(buckets), 1)
        gap = 0.2
        bw = (slide_w - 2 * margin - gap * (n - 1)) / n
        by = self._body_top(bool(spec.get("framing_line"))) + 0.5
        bh = 3.5

        for i, b in enumerate(buckets):
            x = margin + i * (bw + gap)
            box = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Inches(x), Inches(by), Inches(bw), Inches(bh)
            )
            box.fill.solid()
            box.fill.fore_color.rgb = hex_to_rgb(self.palette["neutral_light"])
            box.line.color.rgb = hex_to_rgb(self.palette["neutral_mid"])
            box.line.width = Pt(0.5)

            # Header band
            band = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Inches(x), Inches(by), Inches(bw), Inches(0.6)
            )
            band.fill.solid()
            band.fill.fore_color.rgb = hex_to_rgb(self.palette["accent"])
            band.line.fill.background()

            self._add_text(
                slide,
                x + 0.15,
                by + 0.1,
                bw - 0.3,
                0.45,
                b.get("name", f"Bucket {i + 1}"),
                font_size=14,
                bold=True,
                color_hex="#FFFFFF",
                anchor=MSO_ANCHOR.MIDDLE,
            )

            self._add_text(
                slide,
                x + 0.2,
                by + 0.8,
                bw - 0.4,
                1.5,
                b.get("description", ""),
                font_size=11,
                color_hex=self.palette["body_text"],
            )

            metric = b.get("metric")
            if metric:
                self._add_text(
                    slide,
                    x + 0.2,
                    by + bh - 0.7,
                    bw - 0.4,
                    0.5,
                    metric,
                    font_size=18,
                    bold=True,
                    color_hex=self.palette["accent"],
                )

        self._add_footer(slide, spec.get("source"))

    def render_comparison(self, spec):
        slide = self._blank_slide()
        margin = self.style["slide"]["margin_in"]
        sp = self.style["spacing"]
        slide_w = self.style["slide"]["width_in"]

        self._add_action_title(slide, spec["title"], spec.get("framing_line"))

        options = spec.get("options", [])
        criteria = spec.get("criteria", [])
        recommended = spec.get("recommended", -1)

        n_cols = len(options) + 1  # first col for criterion names
        n_rows = len(criteria) + 1  # first row for option names

        if n_cols < 2 or n_rows < 2:
            return

        ty = self.style["typography"]
        tx = margin
        avail_w = slide_w - 2 * margin
        col_w = [avail_w * 0.30] + [(avail_w * 0.70) / len(options)] * len(options)
        row_h = 0.5
        body_top = self._body_top(bool(spec.get("framing_line"))) + 0.3

        # Draw header row
        for c in range(n_cols):
            x = tx + sum(col_w[:c])
            y = body_top
            highlight = (c - 1) == recommended
            cell = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(x),
                Inches(y),
                Inches(col_w[c]),
                Inches(row_h),
            )
            if c == 0:
                cell.fill.background()
                cell.line.fill.background()
                continue
            cell.fill.solid()
            cell.fill.fore_color.rgb = hex_to_rgb(
                self.palette["accent"] if highlight else self.palette["neutral_dark"]
            )
            cell.line.fill.background()
            self._add_text(
                slide,
                x,
                y,
                col_w[c],
                row_h,
                options[c - 1],
                font_size=12,
                bold=True,
                color_hex="#FFFFFF",
                align=PP_ALIGN.CENTER,
                anchor=MSO_ANCHOR.MIDDLE,
            )

        # Body rows
        for r, crit in enumerate(criteria):
            y = body_top + (r + 1) * row_h
            # Criterion name
            self._add_text(
                slide,
                tx,
                y,
                col_w[0],
                row_h,
                crit.get("name", ""),
                font_size=11,
                bold=True,
                color_hex=self.palette["body_text"],
                anchor=MSO_ANCHOR.MIDDLE,
            )
            ratings = crit.get("ratings", [])
            for c, rating in enumerate(ratings):
                x = tx + sum(col_w[: c + 1])
                highlight = c == recommended
                cell_color = (
                    self.palette["neutral_light"] if (r % 2 == 0) else "#F8F8F8"
                )
                cell = slide.shapes.add_shape(
                    MSO_SHAPE.RECTANGLE,
                    Inches(x),
                    Inches(y),
                    Inches(col_w[c + 1]),
                    Inches(row_h),
                )
                cell.fill.solid()
                cell.fill.fore_color.rgb = hex_to_rgb(cell_color)
                cell.line.color.rgb = hex_to_rgb(self.palette["neutral_mid"])
                cell.line.width = Pt(0.25)

                self._add_text(
                    slide,
                    x,
                    y,
                    col_w[c + 1],
                    row_h,
                    str(rating),
                    font_size=11,
                    bold=highlight,
                    color_hex=(
                        self.palette["accent"]
                        if highlight
                        else self.palette["body_text"]
                    ),
                    align=PP_ALIGN.CENTER,
                    anchor=MSO_ANCHOR.MIDDLE,
                )

        # Recommended badge
        if 0 <= recommended < len(options):
            badge_x = tx + sum(col_w[: recommended + 1])
            badge_y = body_top - 0.4
            self._add_text(
                slide,
                badge_x,
                badge_y,
                col_w[recommended + 1],
                0.3,
                "▼ RECOMMENDED",
                font_size=10,
                bold=True,
                color_hex=self.palette["accent"],
                align=PP_ALIGN.CENTER,
            )

        self._add_footer(slide, spec.get("source"))

    def render_quote(self, spec):
        slide = self._blank_slide()
        margin = self.style["slide"]["margin_in"]
        slide_w = self.style["slide"]["width_in"]
        slide_h = self.style["slide"]["height_in"]

        # Big quote centered
        qt = spec.get("quote", "")
        attribution = spec.get("attribution", "")
        self._add_text(
            slide,
            margin + 1,
            slide_h / 2 - 1.5,
            slide_w - 2 * margin - 2,
            2.5,
            f'"{qt}"',
            font_size=22,
            color_hex=self.palette["body_text"],
            align=PP_ALIGN.CENTER,
            anchor=MSO_ANCHOR.MIDDLE,
        )
        if attribution:
            self._add_text(
                slide,
                margin + 1,
                slide_h / 2 + 1.2,
                slide_w - 2 * margin - 2,
                0.5,
                f"— {attribution}",
                font_size=14,
                color_hex=self.palette["neutral_dark"],
                align=PP_ALIGN.CENTER,
            )

        self._add_footer(slide, spec.get("source"))

    def render_value_chain(self, spec):
        slide = self._blank_slide()
        margin = self.style["slide"]["margin_in"]
        sp = self.style["spacing"]
        slide_w = self.style["slide"]["width_in"]

        self._add_action_title(slide, spec["title"], spec.get("framing_line"))

        steps = spec.get("steps", [])
        n = max(len(steps), 1)
        gap = 0.1
        sw = (slide_w - 2 * margin - gap * (n - 1)) / n
        sy = self._body_top(bool(spec.get("framing_line"))) + 0.5
        sh = 1.0

        for i, step in enumerate(steps):
            x = margin + i * (sw + gap)
            shape = slide.shapes.add_shape(
                MSO_SHAPE.PENTAGON, Inches(x), Inches(sy), Inches(sw), Inches(sh)
            )
            shape.fill.solid()
            shape.fill.fore_color.rgb = hex_to_rgb(self.palette["accent"])
            shape.line.fill.background()
            self._add_text(
                slide,
                x,
                sy,
                sw - 0.3,
                sh,
                step.get("name", ""),
                font_size=12,
                bold=True,
                color_hex="#FFFFFF",
                align=PP_ALIGN.CENTER,
                anchor=MSO_ANCHOR.MIDDLE,
            )
            # Description below
            self._add_text(
                slide,
                x,
                sy + sh + 0.15,
                sw,
                1.5,
                step.get("description", ""),
                font_size=10,
                color_hex=self.palette["body_text"],
                align=PP_ALIGN.LEFT,
            )

        self._add_footer(slide, spec.get("source"))

    def render_roadmap(self, spec):
        slide = self._blank_slide()
        margin = self.style["slide"]["margin_in"]
        sp = self.style["spacing"]
        slide_w = self.style["slide"]["width_in"]

        self._add_action_title(slide, spec["title"], spec.get("framing_line"))

        phases = spec.get("phases", [])
        n = max(len(phases), 1)
        gap = 0.15
        pw = (slide_w - 2 * margin - gap * (n - 1)) / n
        py = self._body_top(bool(spec.get("framing_line"))) + 0.3
        ph = 4.0

        for i, phase in enumerate(phases):
            x = margin + i * (pw + gap)
            # Phase header
            head = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Inches(x), Inches(py), Inches(pw), Inches(0.6)
            )
            head.fill.solid()
            head.fill.fore_color.rgb = hex_to_rgb(self.palette["accent"])
            head.line.fill.background()
            self._add_text(
                slide,
                x,
                py,
                pw,
                0.6,
                phase.get("name", f"Phase {i + 1}"),
                font_size=14,
                bold=True,
                color_hex="#FFFFFF",
                align=PP_ALIGN.CENTER,
                anchor=MSO_ANCHOR.MIDDLE,
            )

            # Body
            body = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(x),
                Inches(py + 0.6),
                Inches(pw),
                Inches(ph - 0.6),
            )
            body.fill.solid()
            body.fill.fore_color.rgb = hex_to_rgb(self.palette["neutral_light"])
            body.line.fill.background()

            # Milestones as bullets
            milestones = phase.get("milestones", [])
            tb = slide.shapes.add_textbox(
                Inches(x + 0.15), Inches(py + 0.75), Inches(pw - 0.3), Inches(ph - 0.85)
            )
            tf = tb.text_frame
            tf.word_wrap = True
            for j, m in enumerate(milestones):
                p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
                p.text = f"•  {m}"
                for run in p.runs:
                    run.font.size = Pt(11)
                    run.font.color.rgb = hex_to_rgb(self.palette["body_text"])
                p.space_after = Pt(6)

        self._add_footer(slide, spec.get("source"))

    def render_section_divider(self, spec):
        slide = self._blank_slide()
        slide_w = self.style["slide"]["width_in"]
        slide_h = self.style["slide"]["height_in"]
        # Big section title centered, accent color, with a horizontal rule
        self._add_text(
            slide,
            1,
            slide_h / 2 - 0.5,
            slide_w - 2,
            1.0,
            spec.get("title", "Section"),
            font_size=32,
            bold=True,
            color_hex=self.palette["accent"],
            align=PP_ALIGN.CENTER,
            anchor=MSO_ANCHOR.MIDDLE,
        )
        # Accent rule
        rule = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(slide_w / 2 - 1),
            Inches(slide_h / 2 + 0.5),
            Inches(2),
            Inches(0.05),
        )
        rule.fill.solid()
        rule.fill.fore_color.rgb = hex_to_rgb(self.palette["accent"])
        rule.line.fill.background()
        # Section dividers don't get a footer

    def render_chart_placeholder(self, spec):
        """Renders a slide with a labelled placeholder. Charts with real data
        should be built by Claude using a data-aware tool (matplotlib, the pptx
        skill, or pasting a chart image) rather than this script."""
        slide = self._blank_slide()
        margin = self.style["slide"]["margin_in"]
        sp = self.style["spacing"]
        slide_w = self.style["slide"]["width_in"]

        self._add_action_title(slide, spec["title"], spec.get("framing_line"))

        # Placeholder rectangle
        x = margin
        y = self._body_top(bool(spec.get("framing_line"))) + 0.3
        w = slide_w - 2 * margin
        h = self.style["slide"]["height_in"] - y - 1.5
        ph = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
        )
        ph.fill.solid()
        ph.fill.fore_color.rgb = hex_to_rgb(self.palette["neutral_light"])
        ph.line.color.rgb = hex_to_rgb(self.palette["neutral_mid"])
        ph.line.width = Pt(0.5)
        self._add_text(
            slide,
            x,
            y,
            w,
            h,
            spec.get("placeholder_text", "[ Chart placeholder — insert chart here ]"),
            font_size=14,
            color_hex=self.palette["neutral_mid"],
            align=PP_ALIGN.CENTER,
            anchor=MSO_ANCHOR.MIDDLE,
        )
        # Caption / takeaway
        if spec.get("caption"):
            self._add_text(
                slide,
                x,
                y + h + 0.1,
                w,
                0.4,
                spec["caption"],
                font_size=11,
                color_hex=self.palette["neutral_dark"],
            )

        self._add_footer(slide, spec.get("source"))

    # ----- dispatch -----

    RENDERERS = {
        "title": "render_title",
        "exec_summary": "render_exec_summary",
        "bullets": "render_bullets",
        "two_by_two": "render_two_by_two",
        "mece_buckets": "render_mece_buckets",
        "comparison": "render_comparison",
        "quote": "render_quote",
        "value_chain": "render_value_chain",
        "roadmap": "render_roadmap",
        "section": "render_section_divider",
        "section_divider": "render_section_divider",
        "chart": "render_chart_placeholder",
        "chart_placeholder": "render_chart_placeholder",
    }

    def build(self, output_path: Path):
        for spec in self.story.get("slides", []):
            stype = spec.get("type")
            method_name = self.RENDERERS.get(stype)
            if not method_name:
                print(f"WARN: unknown slide type: {stype}", file=sys.stderr)
                continue
            if stype != "title":
                self._page_num += 1
            getattr(self, method_name)(spec)
        self.prs.save(str(output_path))


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main():
    p = argparse.ArgumentParser(
        description="Build an MBB-style .pptx from a storyline JSON"
    )
    p.add_argument("storyline", type=Path, help="Path to storyline JSON file")
    p.add_argument("--out", type=Path, default=None, help="Output .pptx path")
    p.add_argument(
        "--palette",
        choices=["navy", "red", "green", "neutral"],
        default=None,
        help="Override the palette in the storyline meta",
    )
    args = p.parse_args()

    if not args.storyline.exists():
        print(f"ERROR: storyline not found: {args.storyline}", file=sys.stderr)
        sys.exit(1)

    storyline = json.loads(args.storyline.read_text())
    out = args.out or args.storyline.with_suffix(".pptx")

    builder = DeckBuilder(storyline, palette_name=args.palette)
    builder.build(out)
    print(f"Built deck: {out}")


if __name__ == "__main__":
    main()
