import struct, zlib, math
import tkinter as tk

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

# --- 3D Cube ---
cube_vertices = [
    [-1,-1,-1], [1,-1,-1], [1,1,-1], [-1,1,-1],
    [-1,-1,1], [1,-1,1], [1,1,1], [-1,1,1]
]
cube_edges = [
    (0,1),(1,2),(2,3),(3,0),
    (4,5),(5,6),(6,7),(7,4),
    (0,4),(1,5),(2,6),(3,7)
]

def rotate_point(x,y,z,ax,ay,az):
    y,z = y*math.cos(ax)-z*math.sin(ax), y*math.sin(ax)+z*math.cos(ax)
    x,z = x*math.cos(ay)+z*math.sin(ay), -x*math.sin(ay)+z*math.cos(ay)
    x,y = x*math.cos(az)-y*math.sin(az), x*math.sin(az)+y*math.cos(az)
    return x,y,z

def project(x,y,z,width,height):
    f = 150
    factor = f / (z+5)
    px = int(width/2 + x*factor*50)
    py = int(height/2 - y*factor*50)
    return px, py

def draw_frame(width, height, angle):
    frame = bytearray(width*height*3)
    for i in range(0,len(frame),3):
        frame[i:i+3] = bytes([20,20,40])
    
    verts = [rotate_point(*v, angle, angle/2, angle/3) for v in cube_vertices]
    verts_2d = [project(*v,width,height) for v in verts]
    
    for e in cube_edges:
        x0,y0 = verts_2d[e[0]]
        x1,y1 = verts_2d[e[1]]
        dx = abs(x1-x0)
        dy = abs(y1-y0)
        sx = 1 if x0<x1 else -1
        sy = 1 if y0<y1 else -1
        err = dx-dy
        while True:
            if 0<=x0<width and 0<=y0<height:
                idx = (y0*width + x0)*3
                frame[idx:idx+3] = bytes([255,200,50])
            if x0==x1 and y0==y1: break
            e2 = 2*err
            if e2> -dy:
                err -= dy
                x0 += sx
            if e2<dx:
                err += dx
                y0 += sy
    return frame

# --- Generate MVP ---
def generate_cube_mvp():
    width,height=200,200
    frames=[]
    for i in range(30):
        angle = i*math.pi/15
        frames.append(draw_frame(width,height,angle))
    write_mvp("cube.mvp", frames, width, height, fps=10)
    print("Generated cube.mvp")

# --- MVP Player ---
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

# --- Run ---
if __name__=="__main__":
    generate_cube_mvp()
    root = tk.Tk()
    root.title("3D Cube MVP Player")
    MVPPlayer(root,"cube.mvp")
    root.mainloop()
