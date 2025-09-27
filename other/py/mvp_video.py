#!/usr/bin/env python3
"""
mvp_codec.py

A pure-stdlib, self-contained lightweight "video" writer + player.
Produces a compact .mvp container storing zlib-compressed frame deltas.
Not MP4/H.264 — but demonstrates codec ideas and is base-python only.

Usage:
  python mvp_codec.py write out.mvp   # produce demo file
  python mvp_codec.py play out.mvp    # play it (Tkinter window)
"""

from __future__ import print_function
import sys, struct, zlib, tempfile, os, time
from math import sqrt, sin
from random import random, seed
seed(0)

# ----------------- frame utilities (RGB bytearrays) -----------------
def make_demo_frame(w,h,t):
    """Generate a demo RGB frame as bytes (row-major r,g,b)."""
    out = bytearray(w*h*3)
    cx,cy = w//2, int(h*0.66)
    maxr = min(w,h)*0.35
    for y in range(h):
        ty = y / float(h-1)
        for x in range(w):
            dx = x - cx
            dy = y - cy
            dist = sqrt(dx*dx + dy*dy)
            glow = max(0.0, 1.0 - dist/maxr)
            # animated offset
            anim = 0.3*(0.5 + 0.5*sin(t*2.0 + dist*0.02))
            r = int( (20 + 220* (ty**1.2)) * (1 - 0.6*glow) + 255*glow*anim )
            g = int( (12 + 120* (ty**1.1)) * (1 - 0.6*glow) + 160*glow*anim )
            b = int( (8 + 40*(ty**1.3)) * (1 - 0.6*glow) + 40*glow*anim )
            i = 3*(y*w + x)
            out[i]   = max(0,min(255,r))
            out[i+1] = max(0,min(255,g))
            out[i+2] = max(0,min(255,b))
    return bytes(out)

def delta_frame(prev_bytes, cur_bytes):
    """Compute simple bytewise delta between prev and cur (XOR could be used; we use subtraction modulo 256).
       Returns bytes representing delta = (cur - prev) mod 256."""
    if prev_bytes is None:
        return cur_bytes  # keyframe: store raw
    # produce delta as bytes
    pb = prev_bytes
    cb = cur_bytes
    assert len(pb) == len(cb)
    out = bytearray(len(cb))
    for i in range(len(cb)):
        out[i] = (cb[i] - pb[i]) & 0xFF
    return bytes(out)

def apply_delta(prev_bytes, delta_bytes):
    """Reconstruct cur = prev + delta (mod 256). If prev is None, delta is raw frame."""
    if prev_bytes is None:
        return delta_bytes
    pb = prev_bytes
    db = delta_bytes
    out = bytearray(len(db))
    for i in range(len(db)):
        out[i] = (pb[i] + db[i]) & 0xFF
    return bytes(out)

# ----------------- container format (.mvp) -----------------
# header: 4s magic 'MVP1' | uint16 width | uint16 height | uint16 fps | uint32 framecount
# follow frames: for each frame: uint32 compressed_length | compressed_data

def write_mvp(path, width, height, fps, frames_bytes):
    """frames_bytes: list of raw RGB frame bytes"""
    with open(path,'wb') as f:
        f.write(b'MVP1')
        f.write(struct.pack('<HHH', width, height, fps))
        f.write(struct.pack('<I', len(frames_bytes)))
        prev = None
        for raw in frames_bytes:
            delta = delta_frame(prev, raw)
            comp = zlib.compress(delta)
            f.write(struct.pack('<I', len(comp)))
            f.write(comp)
            prev = raw

def read_mvp(path):
    """Yield metadata and generator of decompressed frames (reconstructed)."""
    with open(path,'rb') as f:
        magic = f.read(4)
        if magic != b'MVP1':
            raise ValueError("Not MVP1")
        width, height, fps = struct.unpack('<HHH', f.read(6))
        framecount = struct.unpack('<I', f.read(4))[0]
        frames = []
        prev = None
        for i in range(framecount):
            clen = struct.unpack('<I', f.read(4))[0]
            comp = f.read(clen)
            delta = zlib.decompress(comp)
            cur = apply_delta(prev, delta)
            frames.append(cur)
            prev = cur
        return width, height, fps, frames

# ----------------- PPM write (tiny) and Tkinter display -----------------
def write_ppm_bytes(rgb_bytes, w,h):
    """Return bytes of a P6 PPM file for given RGB buffer (not writing to disk)."""
    header = "P6\n{} {}\n255\n".format(w,h).encode('ascii')
    return header + rgb_bytes

def play_mvp(path):
    import tkinter as tk
    from tempfile import NamedTemporaryFile
    width,height,fps,frames = read_mvp(path)
    delay = int(1000.0 / fps)
    root = tk.Tk()
    root.title("MVP Player - " + os.path.basename(path))
    canvas = tk.Canvas(root, width=width, height=height, bg='black')
    canvas.pack()
    img_container = {'tkimg': None}
    tmpfiles = []

    def show_frame(index=[0]):
        i = index[0]
        if i >= len(frames):
            root.destroy()
            # cleanup
            for p in tmpfiles:
                try: os.remove(p)
                except: pass
            return
        rgb = frames[i]
        # write PPM to a temporary file (PhotoImage accepts PPM via file)
        tmp = NamedTemporaryFile(delete=False, suffix='.ppm')
        tmp.write(write_ppm_bytes(rgb, width, height))
        tmp.close()
        tmpfiles.append(tmp.name)
        # load via PhotoImage
        img = tk.PhotoImage(file=tmp.name)
        img_container['tkimg'] = img  # keep ref
        canvas.create_image(0,0, anchor='nw', image=img)
        index[0] += 1
        root.after(delay, show_frame)

    root.after(0, show_frame)
    root.mainloop()

# ----------------- demo write + play -----------------
def demo_write(path, w=320,h=200,fps=12,frames_count=48):
    frames = []
    t = 0.0
    for n in range(frames_count):
        frames.append(make_demo_frame(w,h,t))
        t += 0.15
    write_mvp(path, w,h,fps, frames)
    print("Wrote", path, " ({}x{}, {} fps, {} frames)".format(w,h,fps,frames_count))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python mvp_codec.py write out.mvp   OR  python mvp_codec.py play out.mvp")
        sys.exit(1)
    cmd = sys.argv[1].lower()
    path = sys.argv[2]
    if cmd == 'write':
        demo_write(path)
    elif cmd == 'play':
        play_mvp(path)
    else:
        print("Unknown command")
