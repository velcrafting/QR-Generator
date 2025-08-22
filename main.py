#!/usr/bin/env python3
"""
Branded QR generator (static, no expiration).
- Uses segno to make QR
- Optional centered logo (PNG/JPG/SVG)
- PNG or SVG export
"""
from __future__ import annotations
import io, os, base64, re
from typing import Optional

import segno
from PIL import Image, ImageDraw

try:
    import cairosvg  # optional: rasterize SVG logos or embed logos into SVG output
except Exception:
    cairosvg = None


def _make_qr(data: str, ecc: str = "h", border: int = 3):
    """Return a segno QR object with chosen ECC and border."""
    if ecc not in "lmqh":
        raise ValueError("ecc must be one of l,m,q,h")
    return segno.make(data, error=ecc), {"border": border}


def _paste_logo_on_png(
    img: Image.Image,
    logo_path: str,
    logo_frac: float = 0.22,
    pad: bool = True,
    pad_radius: int = 18,
    pad_margin_px: int = 10,
) -> Image.Image:
    """Overlay a logo at the center of a PNG QR image."""
    W, H = img.size
    ext = os.path.splitext(logo_path.lower())[1]

    # Load logo
    if ext == ".svg":
        if cairosvg is None:
            raise RuntimeError(
                "SVG logo selected but CairoSVG is not available to rasterize it for PNG export.\n"
                "Fix options:\n"
                " - Install system Cairo (conda-forge: cairo pango gdk-pixbuf libffi), or\n"
                " - Use a PNG/JPG logo, or\n"
                " - Export the QR as SVG (vector) instead of PNG."
            )
        raster = cairosvg.svg2png(url=logo_path, output_width=1024, output_height=1024)
        logo = Image.open(io.BytesIO(raster)).convert("RGBA")
    else:
        logo = Image.open(logo_path).convert("RGBA")

    # Resize logo to a fraction of QR width
    target_w = max(1, int(W * logo_frac))
    ratio = target_w / logo.width
    target_h = max(1, int(logo.height * ratio))
    logo = logo.resize((target_w, target_h), Image.LANCZOS)

    # Optional white pad for contrast
    if pad:
        pad_w = target_w + pad_margin_px * 2
        pad_h = target_h + pad_margin_px * 2
        pad_img = Image.new("RGBA", (pad_w, pad_h), (0, 0, 0, 0))
        d = ImageDraw.Draw(pad_img)
        d.rounded_rectangle((0, 0, pad_w, pad_h), pad_radius, fill=(255, 255, 255, 255))
        pad_img.paste(logo, ((pad_w - target_w) // 2, (pad_h - target_h) // 2), logo)
        logo = pad_img
        target_w, target_h = logo.size

    # Paste centered
    x = (W - target_w) // 2
    y = (H - target_h) // 2
    img.paste(logo, (x, y), logo)
    return img


def _embed_logo_in_svg(svg_qr: str, logo_path: str, logo_frac: float = 0.22) -> str:
    """Embed a logo as an <image> inside an SVG QR code."""
    ext = os.path.splitext(logo_path.lower())[1]
    if ext == ".svg":
        with open(logo_path, "rb") as f:
            data = f.read()
        mime = "image/svg+xml"
        b64 = base64.b64encode(data).decode("ascii")
    else:
        img = Image.open(logo_path).convert("RGBA")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        mime = "image/png"

    # Try to parse width/height/viewBox to place accurately
    w_match = re.search(r'width="([\d\.]+)(\w*)"', svg_qr)
    h_match = re.search(r'height="([\d\.]+)(\w*)"', svg_qr)
    vb_match = re.search(r'viewBox="([\d\.\s\-]+)"', svg_qr)

    if not (w_match and h_match and vb_match):
        # Fallback: percentage placement
        width_pct = int(logo_frac * 100)
        inject = (
            f'<image x="50%" y="50%" width="{width_pct}%" height="{width_pct}%" '
            f'href="data:{mime};base64,{b64}" transform="translate(-{width_pct/2}%, -{width_pct/2}%)" />'
        )
        return svg_qr.replace("</svg>", inject + "</svg>")

    vb_x, vb_y, vb_w, vb_h = [float(x) for x in vb_match.group(1).split()]
    logo_w = vb_w * logo_frac
    logo_h = vb_h * logo_frac
    cx = vb_x + vb_w / 2
    cy = vb_y + vb_h / 2
    x = cx - logo_w / 2
    y = cy - logo_h / 2
    inject = f'<image x="{x}" y="{y}" width="{logo_w}" height="{logo_h}" href="data:{mime};base64,{b64}" />'
    return svg_qr.replace("</svg>", inject + "</svg>")


def generate_qr(
    data: str,
    out_path: str,
    *,
    ecc: str = "h",
    border: int = 3,
    scale: int = 12,
    logo_path: Optional[str] = None,
    logo_frac: float = 0.22,
    pad_logo: bool = True,
    pad_radius: int = 18,
    pad_margin_px: int = 10,
) -> str:
    """
    Generate a QR code (PNG or SVG).
    - data: text/URL to encode
    - out_path: file path ending in .png or .svg
    """
    q, _ = _make_qr(data, ecc=ecc, border=border)
    out_lower = out_path.lower()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    if out_lower.endswith(".png"):
        # Render QR to an image and overlay logo if requested
        buf = io.BytesIO()
        q.save(buf, kind="png", border=border, scale=scale)
        buf.seek(0)
        img = Image.open(buf).convert("RGBA")
        if logo_path:
            img = _paste_logo_on_png(img, logo_path, logo_frac, pad_logo, pad_radius, pad_margin_px)
        img.save(out_path)
        return out_path

    if out_lower.endswith(".svg"):
        # Render QR to SVG text and embed logo if requested
        s = io.StringIO()
        q.save(s, kind="svg", border=border)
        svg_txt = s.getvalue()
        if logo_path:
            svg_txt = _embed_logo_in_svg(svg_txt, logo_path, logo_frac)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_txt)
        return out_path

    raise ValueError("out_path must end with .png or .svg")