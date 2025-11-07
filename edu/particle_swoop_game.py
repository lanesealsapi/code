import tkinter as tk
import random
import math

def fade_color(color, alpha):
    """Simulate fading by blending color with black."""
    color = color.lstrip("#")
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    r = int(r * alpha)
    g = int(g * alpha)
    b = int(b * alpha)
    return f"#{r:02x}{g:02x}{b:02x}"

class Particle:
    def __init__(self, canvas, x, y, radius, color):
        self.canvas = canvas
        self.radius = radius
        self.base_radius = radius
        self.color = color
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.alpha = 1.0
        self.id = canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=color, outline=""
        )

    def move(self, width, height, gravity=0):
        self.vy += gravity
        self.x += self.vx
        self.y += self.vy

        # Bounce off walls
        if self.x - self.radius <= 0 or self.x + self.radius >= width:
            self.vx *= -1
        if self.y - self.radius <= 0 or self.y + self.radius >= height:
            self.vy *= -1

        self.canvas.coords(
            self.id,
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius
        )

        # Fade in/out effect
        self.alpha = 0.7 + 0.3 * math.sin(self.x * 0.05 + self.y * 0.05)
        self.canvas.itemconfig(self.id, fill=fade_color(self.color, self.alpha))

    def attract_to(self, mx, my, repelling=False):
        dx = mx - self.x
        dy = my - self.y
        distance = math.hypot(dx, dy)
        if distance < 150 and distance != 0:
            force = (150 - distance) / 1000
            if repelling:
                force *= -1
            self.vx += dx * force
            self.vy += dy * force

    def collide(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        distance = math.hypot(dx, dy)
        if distance == 0:
            return
        if distance < self.radius + other.radius:
            angle = math.atan2(dy, dx)
            total_mass = self.radius + other.radius
            u1 = self.vx * math.cos(angle) + self.vy * math.sin(angle)
            u2 = other.vx * math.cos(angle) + other.vy * math.sin(angle)
            self.vx += (u2 - u1) / total_mass * math.cos(angle)
            self.vy += (u2 - u1) / total_mass * math.sin(angle)
            other.vx += (u1 - u2) / total_mass * math.cos(angle)
            other.vy += (u1 - u2) / total_mass * math.sin(angle)

class Enemy:
    def __init__(self, canvas, width, height, difficulty=1):
        self.canvas = canvas
        self.radius = random.randint(8, 12) * difficulty
        self.x = random.randint(50, width-50)
        self.y = random.randint(50, height-50)
        speed = 1 + difficulty * 0.3
        self.vx = random.uniform(-speed, speed)
        self.vy = random.uniform(-speed, speed)
        self.alpha = 1.0
        self.id = canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill="#ff0000", outline=""
        )

    def move(self, width, height):
        self.x += self.vx
        self.y += self.vy

        if self.x - self.radius <= 0 or self.x + self.radius >= width:
            self.vx *= -1
        if self.y - self.radius <= 0 or self.y + self.radius >= height:
            self.vy *= -1

        self.canvas.coords(
            self.id,
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius
        )

        # Fade effect to reduce blinking
        self.alpha = 0.7 + 0.3 * math.sin(self.x * 0.03 + self.y * 0.03)
        self.canvas.itemconfig(self.id, fill=fade_color("#ff0000", self.alpha))

class ParticleGame:
    def __init__(self, root, num_particles=50, max_enemies=10):
        self.root = root
        self.width = 600
        self.height = 600
        self.gravity = 0.05
        self.repelling = False
        self.colors = ["#00ffea", "#ff00f7"]

        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="#0a0a0a", highlightthickness=0)
        self.canvas.pack()

        # Score
        self.score = 0
        self.score_label = tk.Label(root, text=f"Score: {self.score}", font=("Arial", 16), fg="white", bg="#0a0a0a")
        self.score_label.place(x=10, y=10)

        # Timer
        self.time_left = 60  # seconds
        self.timer_label = tk.Label(root, text=f"Time: {self.time_left}", font=("Arial", 16), fg="white", bg="#0a0a0a")
        self.timer_label.place(x=500, y=10)
        self.root.after(1000, self.update_timer)

        # Particles
        self.particles = [
            Particle(
                self.canvas,
                random.randint(50, self.width - 50),
                random.randint(50, self.height - 50),
                random.randint(5, 12),
                random.choice(self.colors)
            ) for _ in range(num_particles)
        ]

        # Enemies
        self.max_enemies = max_enemies
        self.enemies = [Enemy(self.canvas, self.width, self.height) for _ in range(5)]

        self.mouse_x = self.width / 2
        self.mouse_y = self.height / 2

        self.game_over = False
        self.restart_button = tk.Button(root, text="Restart", font=("Arial", 14), command=self.restart)
        self.restart_button.place(x=250, y=280)
        self.restart_button.lower()  # Hide initially

        self.canvas.bind("<Motion>", self.mouse_move)
        self.root.bind("<space>", self.toggle_repelling)

        self.update()

    def mouse_move(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y

    def toggle_repelling(self, event):
        self.repelling = not self.repelling

    def update_timer(self):
        if self.game_over:
            return
        self.time_left -= 1
        self.timer_label.config(text=f"Time: {self.time_left}")
        if self.time_left <= 0:
            self.end_game()
        else:
            self.root.after(1000, self.update_timer)

    def end_game(self):
        self.game_over = True
        self.restart_button.lift()
        for enemy in self.enemies:
            self.canvas.delete(enemy.id)
        self.enemies.clear()

    def restart(self):
        self.game_over = False
        self.score = 0
        self.time_left = 60
        self.score_label.config(text=f"Score: {self.score}")
        self.timer_label.config(text=f"Time: {self.time_left}")
        self.restart_button.lower()
        self.enemies = [Enemy(self.canvas, self.width, self.height) for _ in range(5)]
        self.root.after(1000, self.update_timer)

    def update(self):
        if not self.game_over:
            # Move enemies
            for enemy in self.enemies:
                enemy.move(self.width, self.height)

            # Move particles
            for i, particle in enumerate(self.particles):
                particle.attract_to(self.mouse_x, self.mouse_y, repelling=self.repelling)
                particle.move(self.width, self.height, gravity=self.gravity)
                for other in self.particles[i+1:]:
                    particle.collide(other)
                for enemy in self.enemies[:]:
                    dx = particle.x - enemy.x
                    dy = particle.y - enemy.y
                    distance = math.hypot(dx, dy)
                    if distance < particle.radius + enemy.radius:
                        # Particle gets used up slightly
                        particle.radius = max(2, particle.radius * 0.9)
                        self.canvas.itemconfig(particle.id, fill=fade_color(particle.color, particle.radius/particle.base_radius))
                        self.canvas.delete(enemy.id)
                        self.enemies.remove(enemy)
                        self.score += 1
                        self.score_label.config(text=f"Score: {self.score}")

            # Increase difficulty
            if len(self.enemies) < self.max_enemies:
                difficulty = 1 + len(self.enemies)//3
                self.enemies.append(Enemy(self.canvas, self.width, self.height, difficulty=difficulty))

            # Game over if enemies exceed max
            if len(self.enemies) > self.max_enemies:
                self.end_game()

        self.root.after(20, self.update)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Particle Smash Game - Fade Edition")
    app = ParticleGame(root)
    root.mainloop()
