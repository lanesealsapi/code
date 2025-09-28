import struct, zlib
import random

# --- MVP Functions ---
def write_mvp(filename, frames, width, height, fps=10):
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

# --- Draw scene frame ---
def draw_frame(width, height, person_x, person_y):
    frame = bytearray(width*height*3)
    
    # --- Background gradient (sky to ground) ---
    for y in range(height):
        for x in range(width):
            idx = (y*width + x)*3
            r = int(135 + (y/height)*50)  # sky to ground gradient
            g = int(206 + (y/height)*40)
            b = int(235 - (y/height)*60)
            frame[idx:idx+3] = bytes([r,g,b])

    # --- River ---
    river_width = 80
    river_center = width//2 + 20
    for y in range(height//2, height):
        for x in range(river_center - river_width//2, river_center + river_width//2):
            if 0<=x<width:
                idx = (y*width + x)*3
                frame[idx:idx+3] = bytes([0, 100 + (y%50), 200 + (y%30)])  # blue gradient

    # --- Trees ---
    num_trees = 5
    for t in range(num_trees):
        tx = 40 + t*70
        ty = height//2 + 10
        # trunk
        for y in range(ty, ty+40):
            for x in range(tx-2, tx+2):
                if 0<=x<width and 0<=y<height:
                    idx = (y*width + x)*3
                    frame[idx:idx+3] = bytes([101, 67, 33])
        # leaves
        for y in range(ty-15, ty):
            for x in range(tx-10, tx+11):
                if 0<=x<width and 0<=y<height:
                    idx = (y*width + x)*3
                    frame[idx:idx+3] = bytes([34,139,34])  # forest green

    # --- Stickman Person ---
    # colors
    head_color = [255,200,200]
    body_color = [255,255,255]
    arm_color = [200,255,200]
    leg_color = [200,200,255]

    # head
    for y in range(person_y-5, person_y+5):
        for x in range(person_x-5, person_x+5):
            if 0<=x<width and 0<=y<height:
                idx = (y*width + x)*3
                frame[idx:idx+3] = bytes(head_color)
    # body
    for y in range(person_y+5, person_y+25):
        x = person_x
        if 0<=x<width and 0<=y<height:
            idx = (y*width + x)*3
            frame[idx:idx+3] = bytes(body_color)
    # arms
    for dx in range(-10,11):
        x = person_x + dx
        y = person_y + 15
        if 0<=x<width and 0<=y<height:
            idx = (y*width + x)*3
            frame[idx:idx+3] = bytes(arm_color)
    # legs
    for dy in range(0,15):
        for lx in [-7, 7]:
            x = person_x + lx
            y = person_y + 25 + dy
            if 0<=x<width and 0<=y<height:
                idx = (y*width + x)*3
                frame[idx:idx+3] = bytes(leg_color)

    return frame

# --- Generate movie ---
def generate_stamp_movie():
    width, height = 400, 600
    frames = []
    for i in range(30):
        person_x = 50 + i*10
        person_y = height//2
        frames.append(draw_frame(width, height, person_x, person_y))
    write_mvp("person_scene.mvp", frames, width, height, fps=10)
    print("Generated Person scene stamp: person_scene.mvp")

# --- MVP Player ---
import tkinter as tk

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

# --- Run demo ---
if __name__ == "__main__":
    generate_stamp_movie()
    root = tk.Tk()
    root.title("Person Scene Stamp Movie")
    MVPPlayer(root, "person_scene.mvp")
    root.mainloop()
