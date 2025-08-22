"""
Configuration for QR Generator.

These are “trusted defaults” — values that usually balance scan reliability
with room for a centered logo. You can tweak them as needed.

Tips:
- Use ECC = 'h' (high) when overlaying logos.
- Border 3–4 modules gives scanners enough quiet zone.
- PNG scale ≥ 12 is safe for print (smaller may blur).
- Logo fraction ~0.18–0.25 (18–25% of QR width) is generally safe.
"""

CONFIG = {
    # Error correction: one of "l", "m", "q", "h"
    "ecc": "h",

    # Quiet zone width (in modules)
    "border": 5,

    # PNG pixel scaling (ignored for SVG)
    "scale": 14,

    # Logo settings
    "logo_frac": 0.22,    # ~22% of QR width
    "pad_logo": True,     # Add white pad for contrast
    "pad_radius": 18,
    "pad_margin_px": 10,
}