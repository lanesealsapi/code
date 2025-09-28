import tkinter as tk
import random

# --- GDP Data ---
past_gdp = [2.1, 2.3, 2.0, 1.8, 2.2, 2.4]
predicted_gdp = [2.2, 2.3, 2.1, 2.0, 2.4, 2.5]

# --- Tkinter Pong Setup ---
WIDTH, HEIGHT = 400, 300
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 50
BALL_SIZE = 10

class GDPPong:
    def __init__(self, root):
        self.root = root
        self.root.title("GDP Pong")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
        self.canvas.pack()

        # Left paddle (past GDP)
        self.left_paddle = self.canvas.create_rectangle(20, HEIGHT/2-PADDLE_HEIGHT/2,
                                                        20+PADDLE_WIDTH, HEIGHT/2+PADDLE_HEIGHT/2,
                                                        fill="blue")
        # Right paddle (predicted GDP)
        self.right_paddle = self.canvas.create_rectangle(WIDTH-30, HEIGHT/2-PADDLE_HEIGHT/2,
                                                         WIDTH-30+PADDLE_WIDTH, HEIGHT/2+PADDLE_HEIGHT/2,
                                                         fill="green")
        # Ball
        self.ball = self.canvas.create_oval(WIDTH/2-BALL_SIZE/2, HEIGHT/2-BALL_SIZE/2,
                                            WIDTH/2+BALL_SIZE/2, HEIGHT/2+BALL_SIZE/2,
                                            fill="yellow")
        # Ball velocity
        self.ball_dx = 4
        self.ball_dy = 3

        # Start animation
        self.animate()

    def move_paddles(self):
        # Move paddles to match GDP values (normalized to HEIGHT)
        left_y = HEIGHT - (past_gdp[-1]/max(past_gdp))*HEIGHT - PADDLE_HEIGHT/2
        right_y = HEIGHT - (predicted_gdp[-1]/max(predicted_gdp))*HEIGHT - PADDLE_HEIGHT/2

        self.canvas.coords(self.left_paddle, 20, left_y, 20+PADDLE_WIDTH, left_y+PADDLE_HEIGHT)
        self.canvas.coords(self.right_paddle, WIDTH-30, right_y, WIDTH-30+PADDLE_WIDTH, right_y+PADDLE_HEIGHT)

    def animate(self):
        self.move_paddles()
        # Move ball
        self.canvas.move(self.ball, self.ball_dx, self.ball_dy)
        bx1, by1, bx2, by2 = self.canvas.coords(self.ball)
        # Bounce off top/bottom
        if by1 <= 0 or by2 >= HEIGHT:
            self.ball_dy *= -1
        # Bounce off paddles
        lp = self.canvas.coords(self.left_paddle)
        rp = self.canvas.coords(self.right_paddle)
        if bx1 <= lp[2] and lp[1] <= by2 <= lp[3]:
            self.ball_dx *= -1
            self.ball_dy += random.uniform(-1,1)
        if bx2 >= rp[0] and rp[1] <= by2 <= rp[3]:
            self.ball_dx *= -1
            self.ball_dy += random.uniform(-1,1)
        self.root.after(30, self.animate)

# --- Run GDP Pong ---
if __name__ == "__main__":
    root = tk.Tk()
    game = GDPPong(root)
    root.mainloop()
