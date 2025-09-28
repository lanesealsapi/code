import tkinter as tk
import struct, zlib

# --- Simple MVP Format Helpers ---
def write_mvp(filename, frames, width, height, fps=10):
    """
    frames: list of raw RGB bytearrays (len = width*height*3)
    """
    with open(filename, "wb") as f:
        f.write(b"MVP1")
        f.write(struct.pack("<IIII", fps, len(frames), width, height))
        for raw in frames:
            comp = zlib.compress(bytes(raw))
            f.write(struct.pack("<I", len(comp)))
            f.write(comp)

def read_mvp(filename):
    with open(filename, "rb") as f:
        if f.read(4) != b"MVP1":
            raise ValueError("Invalid MVP file")
        fps, frame_count, width, height = struct.unpack("<IIII", f.read(16))
        frames = []
        for _ in range(frame_count):
            (size,) = struct.unpack("<I", f.read(4))
            comp = f.read(size)
            raw = zlib.decompress(comp)
            frames.append(raw)
        return fps, width, height, frames

# --- Demo: Generate 1s video of bouncing red square ---
def generate_demo():
    width, height = 160, 120
    square_size = 20
    frames = []
    for i in range(10):  # 1s at 10 fps
        buf = bytearray(width * height * 3)
        x = (i * 10) % (width - square_size)
        y = (i * 7) % (height - square_size)
        for yy in range(square_size):
            for xx in range(square_size):
                px = (y + yy) * width + (x + xx)
                buf[px * 3 + 0] = 255  # Red
                buf[px * 3 + 1] = 0
                buf[px * 3 + 2] = 0
        frames.append(buf)
    write_mvp("demo.mvp", frames, width, height, fps=10)

# --- Tkinter MVP Player ---
class MVPPlayer:
    def __init__(self, root, filename):
        self.root = root
        self.label = tk.Label(root)
        self.label.pack()
        self.fps, self.width, self.height, self.frames = read_mvp(filename)
        self.tkimg = tk.PhotoImage(width=self.width, height=self.height)
        self.label.config(image=self.tkimg)
        self.index = 0
        self.play()

    def play(self):
        raw = self.frames[self.index]
        # Convert raw bytes into "#RRGGBB" rows for put()
        data = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                i = (y * self.width + x) * 3
                r, g, b = raw[i], raw[i+1], raw[i+2]
                row.append(f"#{r:02x}{g:02x}{b:02x}")
            data.append("{" + " ".join(row) + "}")
        self.tkimg.put(" ".join(data))
        self.index = (self.index + 1) % len(self.frames)
        self.root.after(int(1000/self.fps), self.play)

# --- Run demo ---
if __name__ == "__main__":
    generate_demo()
    root = tk.Tk()
    root.title("MVP Player Demo (Pure Python)")
    MVPPlayer(root, "demo.mvp")
    root.mainloop()
