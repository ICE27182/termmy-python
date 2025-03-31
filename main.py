from termmy import ColorBuffer, Vec2i, MSAAoff, MSAAx16, MSAAx8, MSAAx4, MSAAx2, Color

frame_buf = ColorBuffer(80, 40)

frame_buf.fill()

frame_buf.draw_line(Vec2i(30, 30), Vec2i(-64, -128))

frame_buf.draw_line(Vec2i(20, 20), Vec2i(40, 15), 
                    color=Color.from_ints(156, 220, 255))

frame_buf.draw_rect(Vec2i(15, 15), Vec2i(27, 27), fillcolor=True)

frame_buf.set_color(61, 8, Color.from_ints(255, 0, 0))

frame_buf.draw_triangle(Vec2i(4, 4), Vec2i(20, 28), Vec2i(52, 15), 
                        fillcolor=True)

print(frame_buf.ansi_24())

