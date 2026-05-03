from time import sleep, time

from termmy.termiohub import TermIOHub, constants
from termmy.termiohub import InputEvent, KeyboardInput, MouseInput
from termmy.buffers import FrameBuffer, ColorBuffer
from termmy.buffers.color_buffer import ansi24_4x, ansi24
from termmy.render_objects.shapes import *
from termmy.colors import Colors
from termmy.core import Transform

SUPER = True

WIDTH, HEIGHT = 80, 48
if SUPER: WIDTH, HEIGHT = WIDTH * 2, HEIGHT * 2
clrbuf = ColorBuffer(WIDTH, HEIGHT)
fb = FrameBuffer(color_buffer=clrbuf)

oval = Circle(
    WIDTH / 8, 
    ColorBuffer(1,1,(Colors.ice(), )), 
    Transform.identity().translate_to(WIDTH / 2, HEIGHT / 2, 0.0)
    .scale_to(2.0, 1.0, 1.0),
)

pline = PixelLine(
    0.0, 0.0, 23.0, 23.0, Colors.gray(),
)


with TermIOHub() as iohub:
    def print(arg, end=''): iohub.output(arg)
# if True:
    print('\r\n', end='')
    while True:
        
        fb.color_buffer.fill()
        
        oval.render(fb)
        pline.render(fb)
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
                x, y = input.x, input.y
        
        print(f"\033[{HEIGHT // 2 if SUPER else HEIGHT}A", end='')
        sleep(1 / 60)
        