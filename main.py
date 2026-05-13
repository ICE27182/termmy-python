from time import sleep, time
from shutil import get_terminal_size
from subprocess import run

from termmy.termiohub import TermIOHub, constants
from termmy.termiohub import InputEvent, KeyboardInput, MouseInput
from termmy.buffers import FrameBuffer, ColorBuffer
from termmy.buffers.color_buffer import ansi24_4x, ansi24
from termmy.render_objects.shapes import *
from termmy.colors import Colors
from termmy.core import Transform
from termmy.rendering.basic_rendering_functions import rasterize_pixel_point

run("clear", check=True)
run("clear", check=True)

SUPER = False

WIDTH, HEIGHT = 80, 48
# WIDTH, HEIGHT = get_terminal_size()
# WIDTH, HEIGHT = WIDTH // 2, HEIGHT - 2
# if SUPER: WIDTH, HEIGHT = WIDTH * 2, HEIGHT * 2
fb = FrameBuffer.from_size(WIDTH, HEIGHT)

oval = Circle(
    WIDTH / 8, 
    ColorBuffer(1,1,(Colors.ice(), )), 
    Transform.identity().translate_to(WIDTH / 2, HEIGHT / 2, 0.0)
    .scale_to(2.0, 1.0, 1.0),
)

pline = PixelLine(
    0.0, 0.0, 23.0, 23.0, Colors.gray(),
)

point = (0.0, 0.0)
mouse_moved = time()

def pt(arg): print(arg, end='')

with TermIOHub() as iohub:
    def pt(arg): iohub.output(arg)
# if True:
    SHOW_INPUT = 25
    show_input = SHOW_INPUT
    input = ''
    while True:
        now = time()
        
        fb.color_buffer.fill()
        fb.entity_buffer.clear()
        
        oval.render(fb)
        pline.render(fb)
        rasterize_pixel_point(*point, Colors.red(), fb.color_buffer)
        rasterize_pixel_point(1, 1, Colors.cyan() if int(now) & 1 else Colors.blue(), fb.color_buffer)
        if now < mouse_moved:
            rasterize_pixel_point(2, 2, Colors.green(), fb.color_buffer)
        oval.transform.rotate_z_by(0.02)
        
        if SUPER:
            pt(ansi24_4x(fb.color_buffer.width, fb.color_buffer.height, fb.color_buffer.data))
        else:
            pt(ansi24(fb.color_buffer.width, fb.color_buffer.height, fb.color_buffer.data))
        pt(f"\r\n{now}")
        
        match iohub.get_input():
            case InputEvent(input=KeyboardInput(raw=b'Q') 
                            | constants.PredefinedKeys.C_CTRL.value 
                            as kb_input):
                pt(f"\033[{HEIGHT // 2 if SUPER else HEIGHT + 1}B\r\n")
                break
            case InputEvent(input=MouseInput(button=MouseInput.Button.LEFT) as ms_input):
                # You can drag the oval around with the left mouse button
                x, y = ms_input.x, ms_input.y
                if SUPER:
                    y *= 2
                else:
                    x /= 2
                if fb.entity_buffer.get_entity(int(x), y) is oval:
                    oval.transform.translate_to(x, y, 0.0)
                point = (x, y)
            case InputEvent(input=MouseInput(moving=True)):
                mouse_moved = now + 0.2
        
        pt(f"\033[{HEIGHT // 2 if SUPER else HEIGHT + 1}A\r")
        sleep(1 / 1000)
        