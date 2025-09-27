import tkinter as tk
import struct, zlib

# --- GDP Data & Prediction ---
gdp_data = [2.1, 2.3, 2.0, 1.8, 2.2, 2.4, 2.1, 2.3, 2.5, 2.6, 2.4, 2.5]

def predict_next(gdp, months=3):
    predictions = []
    history = gdp[:]
    for _ in range(months):
        next_val = sum(history[-2:])/2
        predictions.append(next_val)
        history.append(next_val)
    return predictions

predicted = predict_next(gdp_data, 3)
full_series = gdp_data + predicted

# --- MVP Video Format ---
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

# --- Generate frames for GDP plot animation ---
def generate_gdp_frames(series, width=400, height=300, padding=40):
    frames = []
    min_val = min(series)
    max_val = max(series)
    n = len(series)

    for end in range(1, n+1):  # build frames incrementally
        # create raw RGB buffer
        buf = bytearray(width*height*3)
        # fill background black
        for i in range(0, len(buf), 3):
            buf[i], buf[i+1], buf[i+2] = 0,0,0
        # draw axes (white)
        for x in range(width):
            buf[(height-padding-1)*width*3 + x*3 : (height-padding-1)*width*3 + x*3+3] = bytes([255,255,255])
        for y in range(height):
            idx = (y*width + padding)*3
            buf[idx:idx+3] = bytes([255,255,255])
        # draw series lines
        points = []
        for i,val in enumerate(series[:end]):
            x = padding + i*(width-2*padding)/(n-1)
            y = height - padding - (val - min_val)/(max_val - min_val)*(height-2*padding)
            points.append((int(x), int(y)))
        for i in range(len(points)-1):
            x0,y0 = points[i]
            x1,y1 = points[i+1]
            # simple line drawing: horizontal and vertical
            for xi in range(min(x0,x1), max(x0,x1)+1):
                if 0 <= xi < width and 0 <= y0 < height:
                    idx = (y0*width + xi)*3
                    buf[idx:idx+3] = bytes([0,255,0] if i>=len(gdp_data)-1 else [0,0,255])
            for yi in range(min(y0,y1), max(y0,y1)+1):
                if 0 <= x1 < width and 0 <= yi < height:
                    idx = (yi*width + x1)*3
                    buf[idx:idx+3] = bytes([0,255,0] if i>=len(gdp_data)-1 else [0,0,255])
        frames.append(buf)
    return frames

# --- Generate MVP "video" ---
frames = generate_gdp_frames(full_series)
write_mvp("gdp_demo.mvp", frames, 400, 300, fps=2)

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
                i = (y*self.width + x)*3
                r,g,b = raw[i], raw[i+1], raw[i+2]
                row.append(f"#{r:02x}{g:02x}{b:02x}")
            rows.append("{" + " ".join(row) + "}")
        self.tkimg.put(" ".join(rows))
        self.index = (self.index + 1) % len(self.frames)
        self.root.after(int(1000/self.fps), self.play)

# --- Run animated plot ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("GDP Growth Animation")
    MVPPlayer(root, "gdp_demo.mvp")
    root.mainloop()
