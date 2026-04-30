#!/usr/bin/env python3
"""
Extrae las imágenes PNG de los outputs del notebook cartográfico y las
guarda en figures/. Se ejecuta automáticamente por GitHub Actions cuando
el notebook cambia en main.

El notebook debe haber sido guardado en Colab con los outputs incluidos
(comportamiento por defecto al guardar tras ejecutar las celdas).
"""
import base64, json, sys
from pathlib import Path

NB_PATH  = Path("notebooks/cartografia_huasco_layout.ipynb")
FIG_DIR  = Path("figures")
FIG_NAME = "mapa_cuenca_huasco.png"

FIG_DIR.mkdir(exist_ok=True)

with open(NB_PATH, encoding="utf-8") as f:
    nb = json.load(f)

extracted = 0
for cell in nb["cells"]:
    if cell["cell_type"] != "code":
        continue
    for output in cell.get("outputs", []):
        data = output.get("data", {})
        if "image/png" not in data:
            continue
        png_b64 = data["image/png"]
        if isinstance(png_b64, list):
            png_b64 = "".join(png_b64)
        png_bytes = base64.b64decode(png_b64)

        # Primera imagen → nombre canónico; adicionales con sufijo numérico
        suffix = "" if extracted == 0 else f"_{extracted + 1}"
        stem   = Path(FIG_NAME).stem
        ext    = Path(FIG_NAME).suffix
        out    = FIG_DIR / f"{stem}{suffix}{ext}"

        out.write_bytes(png_bytes)
        print(f"  ✅ {out}  ({len(png_bytes):,} bytes)")
        extracted += 1

if extracted == 0:
    print("ℹ️  No se encontraron imágenes en los outputs del notebook.")
    print("   Ejecuta el notebook completo en Colab, guárdalo y vuelve a hacer push.")
    sys.exit(0)

print(f"\n✅ {extracted} imagen(es) extraída(s) en {FIG_DIR}/")
