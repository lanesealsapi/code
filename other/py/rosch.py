import tkinter as tk
import random

CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
PARTICLES = 150  # number of ink particles per blot
SPREAD_SPEED = 5  # max pixels particles move per frame

class InkParticle:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        # Random direction
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)

    def move(self):
        # particles move randomly outward
        self.x += self.dx * random.uniform(0, SPREAD_SPEED)
        self.y += self.dy * random.uniform(0, SPREAD_SPEED)

def generate_particles():
    particles.clear()
    canvas.delete("all")
    for _ in range(PARTICLES):
        # start on left half
        x = random.randint(50, CANVAS_WIDTH // 2 - 50)
        y = random.randint(50, CANVAS_HEIGHT - 50)
        size = random.randint(8, 20)
        gray = random.randint(0, 80)
        color = f"#{gray:02x}{gray:02x}{gray:02x}"
        particles.append(InkParticle(x, y, size, color))

def animate():
    canvas.delete("all")
    for p in particles:
        p.move()
        # draw particle on left
        canvas.create_oval(p.x, p.y, p.x + p.size, p.y + p.size, fill=p.color, outline=p.color)
        # mirror to right
        canvas.create_oval(CANVAS_WIDTH - p.x, p.y, CANVAS_WIDTH - p.x + p.size, p.y + p.size, fill=p.color, outline=p.color)
    root.after(50, animate)  # repeat every 50ms

root = tk.Tk()
root.title("Dynamic Rorschach Ink Blot")

canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
canvas.pack()

particles = []

button = tk.Button(root, text="Generate New Blot", command=generate_particles)
button.pack(pady=10)

# start animation loop
animate()

root.mainloop()
