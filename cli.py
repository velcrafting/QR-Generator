#!/usr/bin/env python3
"""
Interactive CLI:
- Prompts for URL/text
- Lets you pick a logo from ./data (optional)
- Lets you choose PNG or SVG and output filename
- Writes to ./output
"""
import os
from pathlib import Path

from config import CONFIG
from main import generate_qr

try:
    import cairosvg  # noqa: F401
    _has_cairosvg = True
except Exception:
    _has_cairosvg = False

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"


def _warn_svg_logo_png_without_cairo(logo_path: str | None, ext: str) -> bool:
    """Return True to abort, False to continue.

    If an SVG logo is selected but PNG output is chosen without CairoSVG,
    prompt the user to either abort or proceed without a logo.
    """
    if not logo_path or ext != ".png":
        return False
    if Path(logo_path).suffix.lower() == ".svg" and not _has_cairosvg:
        print("\nHeads-up: You selected an SVG logo and PNG output, but CairoSVG isn't available.")
        print("Options:\n  1) Switch to SVG output\n  2) Use a PNG/JPG logo\n  3) Install Cairo via conda-forge (cairo pango gdk-pixbuf libffi)")
        choice = (input("Proceed WITHOUT a logo? [y/N]: ").strip().lower() or "n")
        # True = abort, False = continue (dropping the logo happens in main())
        return choice != "y"
    return False


def _pick_logo() -> str | None:
    logos = [p for p in DATA_DIR.glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".svg")]
    if not logos:
        print("No logos found in ./data. Continuing without a logo.")
        return None

    print("\nSelect a logo (or press Enter to skip):")
    for i, p in enumerate(logos, 1):
        print(f"  {i}. {p.name}")
    choice = input("Logo number (blank to skip): ").strip()
    if not choice:
        return None
    try:
        idx = int(choice)
        if 1 <= idx <= len(logos):
            return str(logos[idx - 1])
    except ValueError:
        pass
    print("Invalid selection. Skipping logo.")
    return None


def _ask_output_name(default_stem: str = "qr") -> tuple[str, str]:
    print("\nChoose output format:")
    print("  1. PNG (raster, great for stickers/print)")
    print("  2. SVG (vector, infinite scaling)")
    fmt_choice = input("Format [1/2] (default 1): ").strip() or "1"
    ext = ".png" if fmt_choice == "1" else ".svg"

    stem = input(f"Output file name (without extension) [{default_stem}]: ").strip() or default_stem
    return stem, ext


def main():
    print("=== Branded QR Generator ===")
    data = input("What URL or text should the QR encode? ").strip()
    if not data:
        print("No data entered. Exiting.")
        return

    logo = _pick_logo()

    # Defaults from config
    ecc = CONFIG["ecc"]
    border = CONFIG["border"]
    scale = CONFIG["scale"]
    logo_frac = CONFIG["logo_frac"]
    pad_logo = CONFIG["pad_logo"]

    stem, ext = _ask_output_name(default_stem="qr_code")
    out_path = OUTPUT_DIR / f"{stem}{ext}"

    # Guard: SVG logo + PNG output + no Cairo → offer to abort or continue w/o logo
    abort = _warn_svg_logo_png_without_cairo(logo, ext)
    if abort:
        print("Aborted. Try SVG output or convert your logo to PNG/JPG.")
        return
    if logo and ext == ".png" and Path(logo).suffix.lower() == ".svg" and not _has_cairosvg:
        # User chose to continue without the logo
        logo = None

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        final = generate_qr(
            data=data,
            out_path=str(out_path),
            ecc=ecc,
            border=border,
            scale=scale,
            logo_path=logo,
            logo_frac=logo_frac,
            pad_logo=pad_logo,
            pad_radius=CONFIG["pad_radius"],
            pad_margin_px=CONFIG["pad_margin_px"],
        )
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        return

    print(f"\n✅ Done: {final}")
    print("Tip: test with multiple scanner apps. If scanning is flaky, try a larger border (4),")
    print("a smaller logo (logo_frac 0.18), or keep PNG scale ≥ 12 for print.")


if __name__ == "__main__":
    main()