import tkinter as tk
import random

# Game configuration
CELL_SIZE = 20
COLS = 10
ROWS = 20
PARTICLE_COLORS = ["red", "green", "blue", "yellow", "purple", "cyan"]
INITIAL_SPEED = 500  # milliseconds per step
SPEED_INCREMENT = 20  # speed up per level

class ParticleGame:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=COLS*CELL_SIZE, height=ROWS*CELL_SIZE, bg="black")
        self.canvas.pack()
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.active_particle = None
        self.active_x = COLS // 2
        self.active_y = 0
        self.speed = INITIAL_SPEED
        self.level = 1
        self.score = 0
        self.running = True

        # Bind keys
        root.bind("<Left>", self.move_left)
        root.bind("<Right>", self.move_right)
        root.bind("<Down>", self.move_down)

        self.spawn_particle()
        self.root.after(self.speed, self.game_loop)

    # Spawn a new particle
    def spawn_particle(self):
        color = random.choice(PARTICLE_COLORS)
        self.active_particle = color
        self.active_x = COLS // 2
        self.active_y = 0
        if self.grid[self.active_y][self.active_x]:
            self.running = False  # Game over

    # Draw the grid and active particle
    def draw_grid(self):
        self.canvas.delete("all")
        for y in range(ROWS):
            for x in range(COLS):
                if self.grid[y][x]:
                    self.canvas.create_rectangle(
                        x*CELL_SIZE, y*CELL_SIZE, (x+1)*CELL_SIZE, (y+1)*CELL_SIZE,
                        fill=self.grid[y][x], outline="grey"
                    )
        if self.active_particle:
            self.canvas.create_oval(
                self.active_x*CELL_SIZE, self.active_y*CELL_SIZE,
                (self.active_x+1)*CELL_SIZE, (self.active_y+1)*CELL_SIZE,
                fill=self.active_particle, outline="white"
            )

    # Move left
    def move_left(self, event):
        if self.active_x > 0 and not self.grid[self.active_y][self.active_x-1]:
            self.active_x -= 1

    # Move right
    def move_right(self, event):
        if self.active_x < COLS-1 and not self.grid[self.active_y][self.active_x+1]:
            self.active_x += 1

    # Move down
    def move_down(self, event=None):
        if self.active_y < ROWS-1 and not self.grid[self.active_y+1][self.active_x]:
            self.active_y += 1
        else:
            self.lock_particle()
            self.clear_matches()
            self.spawn_particle()

    # Lock particle into the grid
    def lock_particle(self):
        self.grid[self.active_y][self.active_x] = self.active_particle
        self.active_particle = None

    # Clear horizontal match-3 (or more) and drop remaining particles
    def clear_matches(self):
        to_clear = set()

        # Horizontal match detection
        for y in range(ROWS):
            x = 0
            while x < COLS - 2:
                color = self.grid[y][x]
                if color and self.grid[y][x+1] == color and self.grid[y][x+2] == color:
                    i = x
                    while i < COLS and self.grid[y][i] == color:
                        to_clear.add((y, i))
                        i += 1
                    x = i
                else:
                    x += 1

        # Clear marked cells
        for y, x in to_clear:
            self.grid[y][x] = None
            self.score += 1

        # Drop particles down
        for x in range(COLS):
            column = [self.grid[y][x] for y in range(ROWS) if self.grid[y][x] is not None]
            for y in range(ROWS):
                self.grid[y][x] = None
            for i, color in enumerate(reversed(column)):
                self.grid[ROWS-1-i][x] = color

        # Speed and level adjustment
        if to_clear:
            self.level += 1
            self.speed = max(50, INITIAL_SPEED - SPEED_INCREMENT * (self.level-1))
            # Recursive clearing in case new matches appear after drop
            self.clear_matches()

    # Main game loop
    def game_loop(self):
        if self.running:
            self.move_down()
            self.draw_grid()
            self.root.after(self.speed, self.game_loop)
        else:
            self.canvas.create_text(COLS*CELL_SIZE//2, ROWS*CELL_SIZE//2,
                                    text=f"Game Over\nScore: {self.score}", fill="white", font=("Arial", 20))

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Particle Game 3")
    game = ParticleGame(root)
    root.mainloop()
