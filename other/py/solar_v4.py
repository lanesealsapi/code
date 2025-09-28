import tkinter as tk
import math

class SolarSystemSim:
    def __init__(self, root):
        self.root = root
        self.root.title("Solar System with Box Zoom")
        self.width, self.height = 900, 700

        # Main canvas
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="black")
        self.canvas.pack(fill="both", expand=True)

        # Reset button
        self.reset_btn = tk.Button(root, text="Reset View", command=self.reset_view)
        self.reset_btn.pack(side="bottom", pady=5)

        # Simulation state
        self.default_center_x, self.default_center_y = self.width // 2, self.height // 2
        self.center_x, self.center_y = self.default_center_x, self.default_center_y
        self.scale = 1.0
        self.time = 0

        # Sun, planets, moons
        self.sun = {"r": 20, "color": "yellow"}
        self.planets = [
            {"name": "Mercury", "radius": 5, "orbit": 50, "speed": 0.05, "color": "gray", "moons": []},
            {"name": "Venus",   "radius": 7, "orbit": 90, "speed": 0.035, "color": "orange", "moons": []},
            {"name": "Earth",   "radius": 8, "orbit": 130, "speed": 0.03, "color": "blue",
             "moons": [{"radius": 3, "orbit": 20, "speed": 0.1, "color": "lightgray"}]},
            {"name": "Mars",    "radius": 6, "orbit": 170, "speed": 0.024, "color": "red",
             "moons": [
                 {"radius": 2, "orbit": 12, "speed": 0.15, "color": "gray"},
                 {"radius": 2, "orbit": 18, "speed": 0.12, "color": "darkgray"}
             ]},
            {"name": "Jupiter", "radius": 14, "orbit": 220, "speed": 0.013, "color": "tan",
             "moons": [
                 {"radius": 3, "orbit": 25, "speed": 0.1, "color": "lightblue"},
                 {"radius": 3, "orbit": 30, "speed": 0.08, "color": "white"},
                 {"radius": 4, "orbit": 40, "speed": 0.06, "color": "lightgray"}
             ]}
        ]

        # Drag-zoom state
        self.dragging = False
        self.rect_id = None
        self.start_x = self.start_y = 0

        # Bind mouse
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.animate()

    def reset_view(self):
        """Reset to default zoom and center"""
        self.scale = 1.0
        self.center_x, self.center_y = self.default_center_x, self.default_center_y

    def on_press(self, event):
        self.dragging = True
        self.start_x, self.start_y = event.x, event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="white")

    def on_drag(self, event):
        if self.dragging and self.rect_id:
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        if not self.dragging:
            return
        self.dragging = False
        x0, y0, x1, y1 = self.start_x, self.start_y, event.x, event.y
        if abs(x1 - x0) < 10 or abs(y1 - y0) < 10:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
            return

        # Calculate zoom box
        box_width = abs(x1 - x0)
        box_height = abs(y1 - y0)
        zoom_factor = min(self.width / box_width, self.height / box_height)

        # Update scale and center
        self.scale *= zoom_factor
        self.center_x = (x0 + x1) / 2
        self.center_y = (y0 + y1) / 2

        self.canvas.delete(self.rect_id)
        self.rect_id = None

    def animate(self):
        self.canvas.delete("all")

        # Draw sun
        self.draw_circle(self.width // 2, self.height // 2, self.sun["r"], self.sun["color"])

        # Draw planets and moons
        for planet in self.planets:
            angle = self.time * planet["speed"]
            x = self.width // 2 + math.cos(angle) * planet["orbit"]
            y = self.height // 2 + math.sin(angle) * planet["orbit"]
            self.draw_circle(x, y, planet["radius"], planet["color"])

            # Draw moons
            for moon in planet["moons"]:
                moon_angle = self.time * moon["speed"]
                mx = x + math.cos(moon_angle) * moon["orbit"]
                my = y + math.sin(moon_angle) * moon["orbit"]
                self.draw_circle(mx, my, moon["radius"], moon["color"])

        self.time += 1
        self.root.after(50, self.animate)

    def draw_circle(self, x, y, r, color):
        # Adjust for center/scale
        x, y = (x - self.center_x) * self.scale + self.width // 2, (y - self.center_y) * self.scale + self.height // 2
        r = r * self.scale  # scale radius too
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")

if __name__ == "__main__":
    root = tk.Tk()
    app = SolarSystemSim(root)
    root.mainloop()
