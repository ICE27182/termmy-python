from termmy import *
from termmy.colors.color_quantizer import *
from termmy import ColorMode
from termmy.buffers.msaa_patterns import *
from termmy import display
from math import log10
from time import sleep

display_settings = DisplaySettings.auto_detecting(ensure_lookup_exsits=True)
# display_settings.inverse = True
frame_buf = ColorBuffer(80, 80)
# display_settings.multisampling = MSAAoff
# display_settings.set_color_mode(ColorMode.ANSI256)
display_settings.resize_mode = ResizeMode.AsIs

print(display_settings)

# sleep(0.5)
frame_buf.fill()
display(frame_buf, display_settings, go_back_to_top=True)

# sleep(0.5)
frame_buf.draw_line(Vec2i(30, 30), Vec2i(16, 5))
display(frame_buf, display_settings, go_back_to_top=True)

# sleep(0.5)
frame_buf.draw_line(Vec2i(10, 30), Vec2i(60, 5), 
                    color=Color.from_ints(156, 220, 255),
                    # msaa=MSAAoff,
                    )
display(frame_buf, display_settings, go_back_to_top=True)

# sleep(0.5)
frame_buf.draw_rect(Vec2i(15, 15), Vec2i(27, 27), fillcolor=True)
display(frame_buf, display_settings, go_back_to_top=True)

# sleep(0.5)
frame_buf.set_color(61, 8, Color.from_ints(255, 0, 0))
display(frame_buf, display_settings, go_back_to_top=True)

frame_buf.draw_triangle(Vec2i(4, 4), Vec2i(20, 28), Vec2i(52, 15), 
                        fillcolor=True)
display(frame_buf, display_settings, go_back_to_top=False)
# sleep(0.5)



print(display_settings)

# display(frame_buf, display_settings, go_back_to_top=False)

