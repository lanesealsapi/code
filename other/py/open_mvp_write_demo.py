import struct, zlib
import random

# --- GDP Data ---
past_gdp = [2.1, 2.3, 2.0, 1.8, 2.2, 2.4]
predicted_gdp = [2.2, 2.3, 2.1, 2.0, 2.4, 2.5]

# --- MVP Video Functions ---
def write_mvp(filename, frames, width, height, fps=5):
    with open(filename, "wb") as f:
        f.write(b"MVP1")
        f.write(struct.pack("<IIII", fps, len(frames), width, height))
        for raw in frames:
            comp = zlib.compress(bytes(raw))
            f.write(struct.pack("<I", len(comp)))
            f.write(comp)

# --- Draw frame ---
def draw_frame(width, height, left_y, right_y, ball_x, ball_y, ball_color=(255,255,0)):
    frame = bytearray(width*height*3)
    # background black
    for i in range(0, len(frame), 3):
        frame[i:i+3] = bytes([0,0,0])
    # left paddle
    for y in range(int(left_y), int(left_y)+50):
        for x in range(20,30):
            if 0<=x<width and 0<=y<height:
                idx = (y*width + x)*3
                frame[idx:idx+3] = bytes([0,0,255])
    # right paddle
    for y in range(int(right_y), int(right_y)+50):
        for x in range(width-30,width-20):
            if 0<=x<width and 0<=y<height:
                idx = (y*width + x)*3
                frame[idx:idx+3] = bytes([0,255,0])
    # ball
    for y in range(int(ball_y), int(ball_y)+10):
        for x in range(int(ball_x), int(ball_x)+10):
            if 0<=x<width and 0<=y<height:
                idx = (y*width + x)*3
                frame[idx:idx+3] = bytes(ball_color)
    return frame

# --- Simulation ---
WIDTH, HEIGHT = 400, 300
frames = []

# Initial positions
left_y = HEIGHT/2 - 25
right_y = HEIGHT/2 - 25
ball_x = WIDTH/2
ball_y = HEIGHT/2
ball_dx = 5
ball_dy = 3

# Auto-paddle speed
paddle_speed = 4

for frame_num in range(30):
    # Move paddles automatically to hit ball
    if ball_y + 5 > left_y + 25:
        left_y += paddle_speed
    else:
        left_y -= paddle_speed
    if ball_y + 5 > right_y + 25:
        right_y += paddle_speed
    else:
        right_y -= paddle_speed

    # Keep paddles inside canvas
    left_y = max(0, min(HEIGHT-50, left_y))
    right_y = max(0, min(HEIGHT-50, right_y))

    # Move ball
    ball_x += ball_dx
    ball_y += ball_dy

    # Bounce off top/bottom
    if ball_y <= 0 or ball_y+10 >= HEIGHT:
        ball_dy *= -1

    # Bounce off paddles
    if 20 <= ball_x <= 30 and left_y <= ball_y+5 <= left_y+50:
        ball_dx *= -1
        ball_dy += random.uniform(-1,1)
    if WIDTH-30 <= ball_x+10 <= WIDTH-20 and right_y <= ball_y+5 <= right_y+50:
        ball_dx *= -1
        ball_dy += random.uniform(-1,1)

    # Draw frame
    frames.append(draw_frame(WIDTH, HEIGHT, left_y, right_y, ball_x, ball_y))

# --- Save to MVP ---
write_mvp("gdp_pong.mvp", frames, WIDTH, HEIGHT, fps=5)
print("Saved 30-frame GDP Pong animation as gdp_pong.mvp")
