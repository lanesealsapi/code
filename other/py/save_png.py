#!/usr/bin/env python3
"""
save_png.py

Write a PNG (truecolor, 8-bit RGB) using only Python stdlib (works on Python 3.5+).
Produces out.png when run. Clean, minimal, and snappy.

No dependencies.
"""
from __future__ import division, print_function
import struct, zlib, binascii
from math import sqrt

# ---------- PNG chunk helpers ----------
def _crc(chunk_type, data=b''):
    return binascii.crc32(chunk_type + data) & 0xffffffff

def _pack_chunk(chunk_type, data=b''):
    length = struct.pack(">I", len(data))
    crc = struct.pack(">I", _crc(chunk_type, data))
    return length + chunk_type + data + crc

# ---------- PNG writer ----------
def write_png(path, width, height, rgb_bytes):
    """
    Write a PNG file.
    - width, height: image size
    - rgb_bytes: bytes or bytearray of length width*height*3 (RGB row-major)
    """
    assert len(rgb_bytes) == width * height * 3, "rgb_bytes length mismatch"

    png_sig = b'\x89PNG\r\n\x1a\n'
    with open(path, "wb") as f:
        f.write(png_sig)

        # IHDR: width, height, bitdepth=8, colorType=2 (truecolor), compression=0, filter=0, interlace=0
        ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
        f.write(_pack_chunk(b'IHDR', ihdr))

        # Image data: for each scanline, prepend filter byte 0 + raw RGB bytes
        row_bytes = width * 3
        raw = bytearray()
        for y in range(height):
            start = y * row_bytes
            raw.append(0)  # filter type 0 (None)
            raw.extend(rgb_bytes[start:start + row_bytes])

        # compress with zlib (default compression level)
        compressed = zlib.compress(bytes(raw))
        f.write(_pack_chunk(b'IDAT', compressed))

        # IEND
        f.write(_pack_chunk(b'IEND', b''))

# ---------- Simple scene generator (demo) ----------
def make_demo_image(w, h):
    """
    Returns a bytearray of RGB pixels (w*h*3).
    Scene: warm vertical gradient + glowing circular hot spot
    """
    pixels = bytearray(w * h * 3)
    cx, cy = w // 2, int(h * 0.66)
    max_r = min(w, h) * 0.35

    for y in range(h):
        t = y / (h - 1)
        # background gradient: dark top -> warm bottom
        r_bg = int(20 + (220 - 20) * (t ** 1.2))
        g_bg = int(12 + (120 - 12) * (t ** 1.1))
        b_bg = int(8 + (40 - 8) * (t ** 1.3))

        for x in range(w):
            # distance-based glow
            dx = x - cx
            dy = y - cy
            dist = sqrt(dx*dx + dy*dy)
            glow = max(0.0, 1.0 - dist / max_r)  # 0..1
            # core color (hot center)
            r_core = int(255 * (0.6 * glow + 0.4 * (t)))
            g_core = int(160 * (0.5 * glow + 0.3 * t))
            b_core = int(40 * (0.4 * glow + 0.2 * t))

            # blend background and core
            alpha = glow * 0.9  # how much core influences pixel
            r = int((1 - alpha) * r_bg + alpha * r_core)
            g = int((1 - alpha) * g_bg + alpha * g_core)
            b = int((1 - alpha) * b_bg + alpha * b_core)

            idx = 3 * (y * w + x)
            pixels[idx] = max(0, min(255, r))
            pixels[idx + 1] = max(0, min(255, g))
            pixels[idx + 2] = max(0, min(255, b))
    return pixels

# ---------- Example usage ----------
if __name__ == "__main__":
    W, H = 800, 500
    print("Generating demo image ({}x{})...".format(W, H))
    img = make_demo_image(W, H)
    out = "out.png"
    print("Writing", out)
    write_png(out, W, H, img)
    print("Done. Open", out)

