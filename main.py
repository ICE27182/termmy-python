from termmy import FrameBuffer32, Vec2i, MSAAx16, MSAAx8, MSAAx4, MSAAx2

with FrameBuffer32(60, 30) as frame_buf:
    # frame_buf.draw_line(
    #     Vec2i(0, 0), Vec2i(128, 64)
    # )
    # print(frame_buf.colored_string_24())
    # frame_buf.clear()

    # frame_buf.draw_line(
    #     Vec2i(6, 6), Vec2i(6, 12)
    # )
    # print(frame_buf.colored_string_24())
    # frame_buf.clear()

    # frame_buf.draw_line(
    #     Vec2i(6, 6), Vec2i(12, 6)
    # )
    # print(frame_buf.colored_string_24())
    # frame_buf.clear()

    # frame_buf.draw_line(
    #     Vec2i(30, 30), Vec2i(-64, -128)
    # )
    # print(frame_buf.colored_string_24())
    # 
    frame_buf.fill()
    frame_buf.draw_rect(Vec2i(10, 10), Vec2i(20, 20), True)
    # print(frame_buf.colored_string_24())

    frame_buf.draw_triangle(
        Vec2i(4, 4), 
        Vec2i(20, 28), 
        Vec2i(52, 15), 
        fillcolor=True,
        # linecolor=False,
        msaa=MSAAx8,
    )
    print(frame_buf.colored_string_24())

