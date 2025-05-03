from termmy import *
from termmy.colors.color_quantizer import *
from termmy.buffers.msaa_patterns import *
from math import log10
from time import sleep
from random import random
from collections import deque

WIDTH = 80
HEIGHT = 60
ICE = Color.from_ints(156, 220, 255, 127)

display_settings = DisplaySettings.auto_detecting(ensure_lookup_exsits=True)
# display_settings.inverse = True
frame_buf = ColorBuffer(WIDTH, HEIGHT)
frame_buf = ColorBuffer.from_display_settings(display_settings)
# display_settings.multisampling = MSAAoff
# display_settings.set_color_mode(ColorMode.ANSI256)
# display_settings.resize_mode = ResizeMode.AsIs

safe_print(display_settings)

def default():
    frame_buf.fill()
    frame_buf.draw_line(Vec2i(30, 30), Vec2i(16, 5))
    frame_buf.draw_line(Vec2i(10, 30), Vec2i(60, 5), 
                        color=Color.from_ints(156, 220, 255),
                        # msaa=MSAAoff,
                        )
    frame_buf.draw_rect(Vec2i(15, 15), Vec2i(27, 27), fillcolor=True)
    frame_buf.set_color(61, 8, Color.from_ints(255, 0, 0))
    frame_buf.draw_triangle(Vec2i(4, 4), Vec2i(20, 28), Vec2i(52, 15), 
                            fillcolor=True)

default()

current_color = ICE
pos = Vec2i(WIDTH // 2, HEIGHT // 2)
line = deque([copy(pos), copy(pos)], maxlen=2)
triangle = deque([copy(pos), copy(pos), copy(pos)], maxlen=3)
while True:

    frame_buf.fill(Color(random()*0.95, random(), random(), 0.01))
    key = get_key()
    if key:
        if key.match("escape"):
            safe_print("Exiting")
            sleep(1)
            break
        elif key.match("F"):
            frame_buf.fill()
        elif key.match("f"):
            frame_buf.fill(current_color)

        elif key.match("R"):
            current_color = ICE
        elif key.match("r"):
            current_color = Color(random(), random(), random(), random())
        
        elif key.match(" "):
            default()

        elif key.match("up"):
            frame_buf.set_color(pos.x, pos.y, current_color)
            pos.y = (pos.y - 1) % HEIGHT
            frame_buf.set_color(pos.x, pos.y, ICE)
        elif key.match("down"):
            frame_buf.set_color(pos.x, pos.y, current_color)
            pos.y = (pos.y + 1) % HEIGHT
            frame_buf.set_color(pos.x, pos.y, ICE)
        elif key.match("left"):
            frame_buf.set_color(pos.x, pos.y, current_color)
            pos.x = (pos.x - 1) % WIDTH
            frame_buf.set_color(pos.x, pos.y, ICE)
        elif key.match("right"):
            frame_buf.set_color(pos.x, pos.y, current_color)
            pos.x = (pos.x + 1) % WIDTH
            frame_buf.set_color(pos.x, pos.y, ICE)

        elif key.match("l"):
            line.append(copy(pos))
            frame_buf.set_color(pos.x, pos.y, Color(1, 0, 0, 1))
        elif key.match("L"):
            frame_buf.draw_line(line[0], line[1], Color(0,0,0,1))
        
        elif key.match("t"):
            triangle.append(copy(pos))
            frame_buf.set_color(pos.x, pos.y, Color(1, 0, 0, 1))
        elif key.match("T"):
            frame_buf.draw_triangle(triangle[0], triangle[1], triangle[2], True)

    display(frame_buf, display_settings, go_back_to_top=True)

restore_terminal()