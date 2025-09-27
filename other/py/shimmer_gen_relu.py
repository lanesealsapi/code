import random, struct, zlib, tkinter as tk

# --- ReLU helper ---
def relu(x): return x if x > 0 else 0

# --- Tiny Neural Dream function ---
def dream_transform(frame, width, height, weights):
    out = bytearray(len(frame))
    for i in range(0, len(frame), 3):
        r, g, b = frame[i], frame[i+1], frame[i+2]
        val = relu(weights[0]*r + weights[1]*g + weights[2]*b - 128)
        out[i]   = (r + val) % 256
        out[i+1] = (g + val//2) % 256
        out[i+2] = (b + val//3) % 256
    return out

# --- MVP Format (tiny custom video format) ---
def write_mvp(filename, frames, width, height, fps=5):
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
            frames.append(zlib.decompress(comp))
        return fps, width, height, frames

# --- Generate a Blue Cube image ---
def make_blue_cube(width=64, height=64):
    frame = bytearray(width * height * 3)
    for y in range(height):
        for x in range(width):
            i = (y*width+x)*3
            if 16 <= x < 48 and 16 <= y < 48:   # cube region
                frame[i], frame[i+1], frame[i+2] = 50, 50, 200  # blue
            else:
                frame[i], frame[i+1], frame[i+2] = 0, 0, 0      # black bg
    return frame

# --- Generate Dream Sequence from cube ---
def generate_dream_mvp(out_file="dream.mvp"):
    width, height = 64, 64
    base_frame = make_blue_cube(width, height)
    frames = [base_frame]
    weights = [random.uniform(-0.02, 0.02) for _ in range(3)]
    frame = base_frame
    for _ in range(15):
        frame = dream_transform(frame, width, height, weights)
        frames.append(frame)
    write_mvp(out_file, frames, width, height, fps=4)

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
        rows = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                i = (y*self.width+x)*3
                r, g, b = raw[i], raw[i+1], raw[i+2]
                row.append(f"#{r:02x}{g:02x}{b:02x}")
            rows.append("{" + " ".join(row) + "}")
        self.tkimg.put(" ".join(rows))
        self.index = (self.index + 1) % len(self.frames)
        self.root.after(int(1000/self.fps), self.play)

# --- Run demo ---
if __name__ == "__main__":
    generate_dream_mvp("dream.mvp")
    root = tk.Tk()
    root.title("Dreaming Blue Cube")
    MVPPlayer(root, "dream.mvp")
    root.mainloop()
