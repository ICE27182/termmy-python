from termmy import *
from termmy.colors.color_quantizer import *
from termmy.buffers.msaa_patterns import *
from math import log10
from time import sleep, time
from random import random
from collections import deque
from copy import copy
import sys

def clear():
    from os import system
    import sys
    if sys.platform == "win32":
        system("cls")
    else:
        system("clear")


WIDTH = 80
HEIGHT = 60
ICE = Color.from_ints(156, 220, 255, 127)

display_settings = DisplaySettings.auto_detecting(ensure_lookup_exsits=True)
# display_settings.inverse = True
base = ColorBuffer(WIDTH, HEIGHT)
# base = ColorBuffer.from_display_settings(display_settings)
# display_settings.multisampling = MSAAoff
# display_settings.set_color_mode(ColorMode.ANSI256)
# display_settings.resize_mode = ResizeMode.AsIs

print(display_settings)

def default():
    base.fill()
    base.draw_line(Vec2i(30, 30), Vec2i(16, 5))
    base.draw_line(Vec2i(10, 30), Vec2i(60, 5), 
                        color=Color.from_ints(156, 220, 255),
                        # msaa=MSAAoff,
                        )
    base.draw_rect(Vec2i(15, 15), Vec2i(27, 27), fillcolor=True)
    base.set_color(61, 8, Color.from_ints(255, 0, 0))
    base.draw_triangle(Vec2i(4, 4), Vec2i(20, 28), Vec2i(52, 15), 
                            fillcolor=True)
default()

current_color = ICE
pos = Vec2i(WIDTH // 2, HEIGHT // 2)
line = deque([copy(pos), copy(pos)], maxlen=2)
triangle = deque([copy(pos), copy(pos), copy(pos)], maxlen=3)
recording = None
clear()
with Keyboard() as keyboard:
    while True:
        if keyboard.is_recording():
            base.blend_color(4, 4, Color(r=1.0))
        else:
            base.blend_color(4, 4, Color(g=1.0))

        # Controls
        key_event = keyboard.get_key_event()
        # TODO Remove me
        # safe_print(f"\033[F\n\033[F\033[38;2;156;220;255m{str(key_event):200}")
        if key_event:
            key = key_event.key
            if key.match("escape"):
                safe_print("Exiting")
                sleep(0.5)
                break
            # Canvas
            elif key.match("F"):
                base.fill()
            elif key.match("f"):
                base.fill(current_color)
            elif key.match(" "):
                default()
                pos = Vec2i(WIDTH // 2, HEIGHT // 2)

            # Color
            elif key.match("R"):
                current_color = ICE
            elif key.match("r"):
                current_color = Color(random(), random(), random(), random())
            
            # Movement
            elif key.match("up") or key.match("w"):
                base.set_color(pos.x, pos.y, current_color)
                pos.y = (pos.y - 1) % HEIGHT
                base.set_color(pos.x, pos.y, ICE)
            elif key.match("down") or key.match("s"):
                base.set_color(pos.x, pos.y, current_color)
                pos.y = (pos.y + 1) % HEIGHT
                base.set_color(pos.x, pos.y, ICE)
            elif key.match("left") or key.match("a"):
                base.set_color(pos.x, pos.y, current_color)
                pos.x = (pos.x - 1) % WIDTH
                base.set_color(pos.x, pos.y, ICE)
            elif key.match("right") or key.match("d"):
                base.set_color(pos.x, pos.y, current_color)
                pos.x = (pos.x + 1) % WIDTH
                base.set_color(pos.x, pos.y, ICE)

            # Geomerties
            elif key.match("l"):
                line.append(copy(pos))
                base.set_color(pos.x, pos.y, Color(1, 0, 0, 1))
            elif key.match("L"):
                base.draw_line(line[0], line[1], Color(0,0,0,1))
            elif key.match("t"):
                triangle.append(copy(pos))
                base.set_color(pos.x, pos.y, Color(1, 0, 0, 1))
            elif key.match("T"):
                base.draw_triangle(triangle[0], triangle[1], triangle[2], True)

            # Commands
            elif key.match("/"):
                with safe_io():
                    while True:
                        command = input("/").strip()
                        if command.startswith(("echo ", "print ")):
                            content = " ".join(command.split()[1:])
                            print(content)
                        elif command.startswith(("exit", "quit", "Q")):
                            break
                        elif command.startswith("recording"):
                            command = command.split()
                            if command[-1] == "show":
                                print(f"{recording}")
                            elif command[-1] == "save":
                                if not recording:
                                    print(f"No recording to save")
                                else:
                                    with open("KeyboardRecording", "w") as f:
                                        f.write(recording.to_json())
                                        print("Saved recording to "
                                              "`KeyboardRecording` file.")
                            elif command[-1] == "load":
                                with open("KeyboardRecording", "r") as f:
                                    recording = KeyboardRecording.from_json_string(f.read())
                                    print(f"Loaded recording from "
                                          "`KeyboardRecording` file.")
                            else:
                                print(f"{recording}")
                        elif command.startswith("clear"):
                            clear()
                        else:
                            print(f"Unknown command `{command}`")
            
            # Recording
            elif (sys.platform == "win32" and key.match("f7") 
                  or key.match("7")):
                if keyboard.is_recording():
                    recording = keyboard.end_recording(1)
                else:
                    keyboard.start_recording()
            elif (sys.platform == "win32" and key.match("f8") 
                  or key.match("8")):
                if recording:
                    keyboard.replay(recording)
            elif key.match("0"):
                with safe_io():
                    clear()
                    print(f"{recording}")
                    print("-"*base.width)
                    print(f"{keyboard.key_event_buffer=}")
                    getch()
        
        if 1:
            display(base, display_settings, go_back_to_top=True)
        else:
            sleep(1.0/90.0)
            safe_print(base.ansi_24(), end="\033[F"*(HEIGHT))
