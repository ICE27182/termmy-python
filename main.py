from time import sleep, time
from shutil import get_terminal_size

from termmy.termiohub import TermIOHub, constants
from termmy.termiohub import InputEvent, KeyboardInput, MouseInput
from termmy.buffers import FrameBuffer, ColorBuffer
from termmy.buffers.color_buffer import ansi24_4x, ansi24
from termmy.render_objects.shapes import *
from termmy.colors import Colors
from termmy.core import Transform
from termmy.rendering.basic_rendering_functions import rasterize_pixel_point

SUPER = False

WIDTH, HEIGHT = 80, 48
WIDTH, HEIGHT = get_terminal_size()
WIDTH //= 2
if SUPER: WIDTH, HEIGHT = WIDTH * 2, HEIGHT * 2
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


with TermIOHub() as iohub:
    def print(arg, end=''): iohub.output(arg)
# if True:
    print('\r\n', end='')
    SHOW_INPUT = 25
    show_input = SHOW_INPUT
    input = ''
    while True:
        
        fb.color_buffer.fill()
        fb.entity_buffer.clear()
        
        oval.render(fb)
        pline.render(fb)
        rasterize_pixel_point(*point, Colors.red(), fb.color_buffer)
        oval.transform.rotate_z_by(0.02)
        
        if SUPER:
            print(ansi24_4x(fb.color_buffer.width, fb.color_buffer.height, fb.color_buffer.data), end='')
        else:
            print(ansi24(fb.color_buffer.width, fb.color_buffer.height, fb.color_buffer.data), end='')
        print(f"\r\n{time()}", end='')
        
        input_event = iohub.get_input(10)
        if input_event is not None:
            input = input_event.input
            if isinstance(input, KeyboardInput):
                if (input.raw == b"Q"
                    or input == constants.PredefinedKeys.C_CTRL.value):
                    print(f"\033[{HEIGHT+6}B\r\n", end='')
                    break
            elif isinstance(input, MouseInput):
                if input.button == MouseInput.Button.LEFT:
                    x, y = input.x / 2, input.y
                    # if fb.entity_buffer.get_entity(int(x), y) is oval: # TODO update the pixel shader
                    oval.transform.translate_to(x, y, 0.0)
                    point = (x, y)
        
        print(f"\033[{HEIGHT // 2 if SUPER else HEIGHT}A", end='')
        sleep(1 / 60)
        