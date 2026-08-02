"""Desaturate + normalise partner logos for the marquee.

Two things the naive pipeline gets wrong:
  * Some Commons files are CMYK; converting straight to Gray misreads the tones,
    so everything is forced through sRGB first.
  * Marks that ship on a light solid panel (Ritz-Carlton is light blue) keep a
    grey rectangle after desaturation, which reads as a box floating among
    transparent logos. Light panels are flood-filled to white; dark panels
    (Mercure, Novotel, Grand Hyatt, ibis) are left alone, since those marks are
    only legible as white-on-dark.
"""

import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "logos", "raw")
OUT = os.path.join(HERE, "logos", "bw")

BOX_W, BOX_H = 340, 130
FIT_W, FIT_H = 320, 110
LIGHT_PANEL_THRESHOLD = 195  # 0-255; above this the panel reads as "light"


def run(args):
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout.strip()


def corner_luma(path):
    vals = []
    for x, y in ((1, 1), (2, 2)):
        out = run(["magick", path, "-format", f"%[fx:255*p{{{x},{y}}}.r]", "info:"])
        vals.append(float(out))
    return sum(vals) / len(vals)


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(HERE, "_t.png")
    for name in sorted(os.listdir(RAW)):
        if not name.endswith(".png"):
            continue
        src, dst = os.path.join(RAW, name), os.path.join(OUT, name)

        # Desaturate and crop to the mark.
        run(["magick", src, "-colorspace", "sRGB", "-background", "white",
             "-alpha", "remove", "-alpha", "off", "-colorspace", "Gray",
             "-fuzz", "4%", "-trim", "+repage", tmp])

        luma = corner_luma(tmp)
        args = ["magick", tmp]
        if luma > LIGHT_PANEL_THRESHOLD:
            # Light panel: flood the corners to pure white so the mark floats
            # like the transparent logos beside it. Coordinates come from the
            # trimmed size — the canvas is only padded out to BOX_* later, so
            # BOX_W-1 would land outside the image and abort the whole convert.
            w, h = (int(v) for v in run(
                ["magick", tmp, "-format", "%w %h", "info:"]).split())
            for x, y in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
                args += ["-fuzz", "12%", "-fill", "white", "-draw", f"color {x},{y} floodfill"]
        args += ["-resize", f"{FIT_W}x{FIT_H}>", "-gravity", "center",
                 "-background", "white", "-extent", f"{BOX_W}x{BOX_H}",
                 "-strip", "-quality", "92", dst]
        run(args)
        kb = os.path.getsize(dst) / 1024
        print(f"{name[:-4]:16s} panel_luma={luma:6.1f} {'light->white' if luma > LIGHT_PANEL_THRESHOLD else 'kept':13s} {kb:5.1f} KB")

    os.path.exists(tmp) and os.remove(tmp)


if __name__ == "__main__":
    main()
