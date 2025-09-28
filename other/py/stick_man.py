import struct, zlib

# --- MVP Functions ---
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

# --- Draw stickman frame ---
def draw_frame(width, height, person_x, person_y):
    frame = bytearray(width*height*3)
    # black background
    for i in range(0, len(frame), 3):
        frame[i:i+3] = bytes([0,0,0])
    
    # Person stickman: simple lines
    # head
    for y in range(person_y-5, person_y+5):
        for x in range(person_x-5, person_x+5):
            if 0<=x<width and 0<=y<height:
                idx = (y*width + x)*3
                frame[idx:idx+3] = bytes([255,255,255])
    # body
    for y in range(person_y+5, person_y+20):
        x = person_x
        if 0<=x<width and 0<=y<height:
            idx = (y*width + x)*3
            frame[idx:idx+3] = bytes([255,255,255])
    # arms
    for dx in range(-7,8):
        x = person_x + dx
        y = person_y + 10
        if 0<=x<width and 0<=y<height:
            idx = (y*width + x)*3
            frame[idx:idx+3] = bytes([255,255,255])
    # legs
    for dy in range(0,10):
        if 0<=person_x-5<width and 0<=person_y+20+dy<height:
            idx = ((person_y+20+dy)*width + (person_x-5))*3
            frame[idx:idx+3] = bytes([255,255,255])
        if 0<=person_x+5<width and 0<=person_y+20+dy<height:
            idx = ((person_y+20+dy)*width + (person_x+5))*3
            frame[idx:idx+3] = bytes([255,255,255])
    return frame

# --- Generate "stamp" movie ---
def generate_stamp_movie():
    width, height = 160, 80
    frames = []
    for i in range(30):
        person_x = 10 + i*4  # walk horizontally
        person_y = height//2
        frames.append(draw_frame(width, height, person_x, person_y))
    write_mvp("person_stamp.mvp", frames, width, height, fps=10)
    print("Generated Person stamp movie: person_stamp.mvp")

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

# --- Run the demo ---
if __name__ == "__main__":
    generate_stamp_movie()
    root = tk.Tk()
    root.title("Person Stamp Movie")
    MVPPlayer(root, "person_stamp.mvp")
    root.mainloop()
