from termmy import *
from math import pi
from time import sleep

grid = ColorBuffer(40, 40)
for y in range(grid.height):
    for x in range(grid.width):
        grid.set_color(x, y,
                       Colors.magenta()
                       if x // 8 % 2 != y // 8 % 2 else
                       Colors.black())

if __name__ == "__main__" and True:
    base = ColorBuffer(1, 1).fill()
    renderer = Renderer(
        anti_aliasing=None,
    )
    post_effect = PostEffect()
    post_effect.fxaa = 0
    post_effect.invert = 0
    context = RenderContext(104, 52)
    scene = Scene(base)

    bmp = Image.from_image_file("ignored_meal.bmp")
    buffer_fill = SimpleColorBufferFill.from_color_buffer(bmp.buffer)
    scene.base = bmp.buffer
    buffer_fill = BufferFill(bmp, 
                             Transform2D.create_in_degrees(rotation_degrees=30, 
                                                           pivot=Vec2(bmp.width/2, bmp.height/2),
                                                           scale=1/3))
    # buffer_fill = SimpleColorBufferFill.from_color_buffer(grid)
    scene.base = grid

    circle = Circle.at(
        x=15.0, 
        y=30.0, 
        radius=12.0, 
        z=1.0, 
        fill=LinearFill.from_colors(
            Colors.red(),
            Colors.green(),
            Colors.blue(),
            Colors.ice(),
        )
    )
    circle.transform.inheritance = (
        TransformInheritance.NONE
        | TransformInheritance.TRANSLATE
        | TransformInheritance.SCALE
        | TransformInheritance.ROTATE
    )
    circle.stroke = SimpleStroke(SolidFill(Colors.ice()), circle)
    
    grid_dots = (
        Node(transform=Transform2D(
                pivot=Vec2(35.0, 25.0),
            ))
            .add_child(Dot.at(x=5.0, y=10.0, z=0.0, fill=SolidFill(Color(1.0, 0.0, 0.0))))
            .add_child(Dot.at(x=10.0, y=10.0, z=2.0, fill=SolidFill(Color(0.5, 0.0, 0.0))))
            .add_child(Dot.at(x=20.0, y=10.0, z=0.0, fill=SolidFill(Color(0.5, 0.5, 0.0))))
            .add_child(Dot.at(x=40.0, y=10.0, z=2.0, fill=SolidFill(Color(0.0, 1.0, 0.0))))

            .add_child(Dot.at(x=5.0, y=30.0, z=0.0, fill=SolidFill(Color(0.0, 0.5, 0.0))))
            .add_child(Dot.at(x=10.0, y=30.0, z=2.0, fill=SolidFill(Color(0.0, 0.5, 0.5))))
            .add_child(Dot.at(x=20.0, y=30.0, z=0.0, fill=SolidFill(Color(0.0, 0.0, 1.0))))
            .add_child(Dot.at(x=40.0, y=30.0, z=2.0, fill=SolidFill(Color(1.0, 0.0, 1.0))))

            .add_child(circle)
    )
    pivot_circle = Circle.at(x=-1.0, y=-1.0, radius=2.0, z=1.0, fill=SolidFill(Color(0.0, 0.0, 0.0)))
    pivot_circle.transform.translate = grid_dots.transform.pivot
    grid_dots.add_child(pivot_circle)
    scene.add_node(grid_dots)

    start = Vertex2(40.0, 25.0, 0.0, 0.0)
    end = Vertex2(20.0, 25.0, 1.0, 1.0)
    scene.add_node(
        Node()
            .add_child(Dot.create_with(start))
            .add_child(Dot.create_with(end))
            .add_child(Line.create_with(
                start=start,
                end=end,
                fill=LinearFill.from_colors(Colors.indigo(),
                                            Colors.ice(),
                                            Colors.lapis_lazuli())
            ))
    )

    tri = Triangle(
        a=Vertex2(0.0, 0.0, 0.0, 0.0),
        b=Vertex2(25.0, 12.0, 1.0, 0.0),
        c=Vertex2(16.0, 16.0, 16/25, 0.0),
        # fill=LinearFill.from_colors(Colors.red(),
        #                                  Colors.green(),
        #                                  Colors.blue()),

        fill = SolidFill(Colors.indigo()),
        transform=Transform2D(translate=Vec2(4.0, 4.0),
                              pivot=Vec2(41 / 3, 15))
    )
    scene.add_node(tri)

    line_start = Vertex2(0.0, 2.0, 0.0, 0.0)
    line_end = Vertex2(50.0, 20.0, 1.0, 1.0)
    line = Line(line_start, line_end, fill=LinearFill.from_colors(Colors.red(), Colors.ice(), Colors.blue()))
    scene.add_node(line)

    ring = Ring(12, 18, LinearFill.from_colors(Colors.ice(), Colors.navy()), 
                transform=Transform2D(translate=Vec2(15, 30)))
    scene.add_node(ring)
    # scene._nodes.clear()
    rectangle = Rectangle(20, 20, buffer_fill, transform=Transform2D(translate=Vec2(60.0, 20.0)))
    scene.add_node(rectangle)

    aa_selection = 0
    aa_pool = [
        None,
        AAAx4,
        AAAx16,
        MSAAx4,
        MSAAx16,
        SSAAx2,
    ]

    shape_selection = 0
    shape_pool = [
        rectangle,
        circle,
        ring,
        line,
        tri,
    ]
    stroke_pool = [s.stroke for s in shape_pool]
    fill_pool = [s.fill for s in shape_pool]
    STROKE = SimpleStroke(fill=LinearFill.from_colors(Colors.red(), Colors.black()), shape=tri)
    clear_screen()
    with Keyboard() as kb:
        while True:
            renderer.initiate_buffer(scene, context)
            renderer.render_nodes(scene, context)
            post_effect.apply(context)
            safe_print(context.color_buffer.ansi_24(), end="\033[F"*context.height)
            # sleep(1/10)

            grid_dots.transform.rotation_radians -= pi / 120

            rotated = Mat2.rotation(pi / 72) * (end - start) + start
            end.x = rotated.x
            end.y = rotated.y

            rectangle.fill.transform.rotation_radians -= pi / 120


            shape_selected: Shape = shape_pool[shape_selection % len(shape_pool)]

            key_event = kb.get_key_event()
            if key_event:
                key = key_event.key
                if key.match("escape"):
                    break
                # AA
                elif key.match(")"):
                    aa_selection += 1
                elif key.match("("):
                    aa_selection -= 1
                elif key.match("-"):
                    aa_selection = 0
                elif key.match("F"):
                    post_effect.fxaa = not post_effect.fxaa
                    
                elif key.match("w"):
                    shape_selected.transform.translate.y -= 1.0
                elif key.match("s"):
                    shape_selected.transform.translate.y += 1.0
                elif key.match("a"):
                    shape_selected.transform.translate.x -= 1.0
                elif key.match("d"):
                    shape_selected.transform.translate.x += 1.0
                elif key.match('q'):
                    shape_selected.transform.rotation_radians -= 1/72
                elif key.match('e'):
                    shape_selected.transform.rotation_radians += 1/72
                elif key.match('f'):
                    shape_selected.transform.scale += 0.1
                elif key.match('v'):
                    shape_selected.transform.scale -= 0.1
                elif key.match('r'):
                    shape_selected.transform.scale = 1.0


                elif key.match("/"):
                    shape_selected.stroke = None
                elif key.match(","):
                    shape_selected.fill = fill_pool[shape_selection]
                elif key.match("."):
                    shape_selected.fill = buffer_fill


                elif key.match("["):
                    shape_selected.stroke = stroke_pool[shape_selection]
                    shape_selection = (shape_selection - 1) % len(shape_pool)
                    shape_selected = shape_pool[shape_selection]
                    shape_selected.stroke = SimpleStroke.from_simple_stroke(STROKE, shape_selected)
                elif key.match("]"):
                    shape_selected.stroke = stroke_pool[shape_selection]
                    shape_selection = (shape_selection + 1) % len(shape_pool)
                    shape_selected = shape_pool[shape_selection]
                    shape_selected.stroke = SimpleStroke.from_simple_stroke(STROKE, shape_selected)
                    
                # Clear
                elif key.match(" "):
                    clear_screen()
                # Mode
                elif key.name.isnumeric():
                    circle.transform.inheritance = int(key.name)

            renderer.anti_aliasing = aa_pool[aa_selection % len(aa_pool)]
            