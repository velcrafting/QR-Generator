# Branded QR Generator (Static, No Expiration)

Generate QR codes locally with a centered brand logo. No tracking, no SaaS, no expiration.

- Static QR image, **destination under your control**
- PNG or SVG output
- Optional centered logo (PNG/JPG, or SVG if CairoSVG is available)
- “Trusted defaults” via `config.py`

---

## Repo Structure

QR_Generator/
├─ main.py # library: generate_qr(...)
├─ cli.py # interactive CLI
├─ config.py # trusted defaults (ECC, border, logo scale, etc.)
├─ requirements.txt # segno, Pillow, (optional) cairosvg
├─ readme.md
├─ data/ # put your logos here (png/jpg/svg)
│ └─ logo.png
└─ output/ # generated codes land here


---

## Prerequisites

- Python 3.10+  
- For **SVG logos with PNG output**, you’ll also need CairoSVG **and** the native Cairo library.
  - Easiest way to avoid that: use a PNG/JPG logo, or export **SVG output**.
  - Proper install (conda):  
    ```bash
    conda install -c conda-forge cairo pango gdk-pixbuf libffi
    ```

---

## Quick Start

```bash
# Clone
git clone https://github.com/<you>/QR_Generator.git
cd QR_Generator

# Optional but recommended: clean virtualenv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install deps
pip install -r requirements.txt

# Run interactive CLI
python cli.py

You’ll be prompted to:

Enter the URL/text to encode

Pick a logo from ./data (optional)

Choose PNG or SVG and name the output

Files are saved to ./output.
```

---

## Configuration

Trusted defaults live in config.py:
```bash
CONFIG = {
    "ecc": "h",        # Error correction (l/m/q/h). 'h' = highest, best for logos
    "border": 3,       # Quiet zone in modules (3-4 recommended)
    "scale": 14,       # PNG pixels per module (>=12 for print)
    "logo_frac": 0.22, # Logo width as fraction of QR width (0.18–0.25 safe)
    "pad_logo": True,  # Add white pad behind logo for contrast
    "pad_radius": 18,
    "pad_margin_px": 10,
}
```
Edit these values to change CLI and library defaults.

---

## Library Use
```bash
from main import generate_qr
from config import CONFIG

generate_qr(
  data="https://example.com",
  out_path="output/example.png",
  ecc=CONFIG["ecc"],
  border=CONFIG["border"],
  scale=CONFIG["scale"],
  logo_path="data/logo.png",          # or .svg if CairoSVG available
  logo_frac=CONFIG["logo_frac"],
  pad_logo=CONFIG["pad_logo"],
  pad_radius=CONFIG["pad_radius"],
  pad_margin_px=CONFIG["pad_margin_px"],
)
```

---

## Tips for Reliable Scanning

- Keep ECC = H when overlaying a logo.
- Use border ≥ 3 (4 is safer for posters).
- For PNG, use scale ≥ 12 so print stays crisp.
- Keep the logo ≤ 25% of QR width (0.18–0.22 is a sweet spot).
- Avoid covering the finder patterns (the three big corner squares) and keep the  Quiet zone intact.
- If scans are unreliable:
 - increase border to 4
 - reduce logo_frac to ~0.18–0.20
 - ensure the white pad is enabled (pad_logo=True)

---

## Troubleshooting (CairoSVG / Cairo)

If you select an SVG logo and PNG output but don’t have Cairo installed, you’ll see a warning.

Options:
- Use a PNG/JPG logo (easiest)
- Choose SVG output (no Cairo needed)
- Install native Cairo (conda-forge):
```bash
conda install -c conda-forge cairo pango gdk-pixbuf libffi
python -c "import cairosvg; print(cairosvg.__version__)"
```
Stuck in a dependency maze? Create a fresh venv, reinstall requirements.txt, and try again.

---

## Potential Improvements (Roadmap)

These are nice future add-ons you—or contributors—can tackle. PRs welcome.

- Dynamic redirects (static visual, changeable destination)
Encode a short URL you own (e.g., https://qr.yourdomain.com/vc1) and update its target later.

 - Edge worker example (Cloudflare Workers): simple slug→URL map with 302 redirects.
 - Netlify _redirects: edit rules, redeploy in seconds.
 - Mini FastAPI service: /{slug} → target, change in a dict/DB. Use 302/307 for changeable destinations.

- Batch generation from CSV
--csv input.csv with columns like data,filename,logo,format. Perfect for campaigns.

- Printable sheets / labels
Auto-layout multiple codes to a PDF (e.g., 3×4 grid with labels). Great for stickers and table tents.

- Auto-tuning density
Choose QR version and error correction based on data length; warn if the logo would over-obscure modules.

- QR validation + test grid
After render, run a quick decode (e.g., qrcode/zbarlight) and produce a small preview grid to sanity-check scanability.

- CLI flags to override config
--border 4 --logo-frac 0.20 --no-pad for one-off runs without editing config.py.

- Content helpers
Built-ins for Wi-Fi (WIFI:T:WPA;S:SSID;P:pass;), mailto:, tel:, vCard/meCard, etc.

- Theming (carefully)
Optional dark/light foreground with contrast checks; rounded modules; quiet color palettes. Guardrails to keep contrast and finder patterns compliant.

- Automatic logo contrast
If logo is dark, increase pad size; if logo is light, add thin border around pad. Aim for consistent luminance contrast.

- Output naming templates
"{slug}_{date}.png" or "{domain}-{shortcode}.svg" via a small templates.py.

- Packaging & DX
 - pip install qr-brand (turn this into a tiny PyPI package)
 - pre-commit hooks (black, ruff)
 - GitHub Actions CI: lint, unit tests, and sample artifact build
 - Optional Dockerfile for zero-friction runs
 - Homebrew tap for qrgen CLI