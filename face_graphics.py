# Author: Matthew Cruise
# Date: 11/12/2026
# Description: Manages the running of the static and moving face animations depending
# on whether the robot voice from robot_voice_with_animation is speaking.
import pygame

# Lambda function that returns false for use in run_face_loop()
_is_speaking = lambda: False

# Returns True when robot is speaking and False when not
def set_speaking_fn(fn):
    global _is_speaking
    _is_speaking = fn

# Draws the robot eyes and mouth
def _draw_eyes_and_mouth(canvas, x, y, mouth_state):
    # Draws static components of the animation
    canvas.fill("white")
    pygame.draw.circle(canvas, "black", (250, 200), 30)
    pygame.draw.circle(canvas, "black", (550, 200), 30)
    rect = pygame.Rect(0, 0, 250, mouth_state)
    rect.center = (x, y)
    pygame.draw.ellipse(canvas, "black", rect, 0)
    pygame.display.flip()

# Runs static face animation loop
def static_face_animation(canvas, frame_clock, fps):
    # Initializes mouth position and state
    x = 400
    y = 400
    mouth_state = 25

    # Animation loop
    while not _is_speaking():
        frame_clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

        _draw_eyes_and_mouth(canvas, x, y, mouth_state)

    return "continue"

# Runs moving face animation loop
def moving_face_animation(canvas, frame_clock, fps):

    # Initializes mouth position, state, speed, and direction
    x = 400
    y = 400
    mouth_open_min = 25
    mouth_open_max = 50
    mouth_state = mouth_open_min
    speed = 130
    direction = 1

    # Animation loop
    while _is_speaking():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

        dt = frame_clock.tick(fps) / 1000
        mouth_state += speed * direction * dt

        if mouth_state >= mouth_open_max:
            mouth_state = mouth_open_max
            direction = -1
        elif mouth_state <= mouth_open_min:
            mouth_state = mouth_open_min
            direction = 1

        _draw_eyes_and_mouth(canvas, x, y, mouth_state)

    return "continue"

# Initializes Pygame and runs either the static or moving face animation loop
# depending on whether _is_speaking() returns True or False
def run_face_loop():
    pygame.init()
    width = 800
    height = 600
    canvas = pygame.display.set_mode((width, height))
    frame_clock = pygame.time.Clock()
    fps = 60

    try:
        while True:
            if _is_speaking():
                status = moving_face_animation(canvas, frame_clock, fps)
            else:
                status = static_face_animation(canvas, frame_clock, fps)

            if status == "quit":
                break
    finally:
        pygame.quit()

def main():
    run_face_loop()

if __name__ == "__main__":
    main()