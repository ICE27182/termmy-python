

from .color import Color
from termmy.core import process_bar

from collections.abc import Iterable
from math import ceil, dist

DEFAULT_ALPHA:int = 255

# color quantization with brute force
def get_color_quantization_table(palette:Iterable[Color], 
                                 box_size:int = 32, 
                                 progress_bar_width:None|int=20) -> bytearray:
    """
    Use brute force to find the color in the palette for all 24bit colors
    (the result will be 3MB)

    Length of `palette` must not exceed 256 because we are using bytes to
    store the result and 8-bit integers are used to index the palette

    `box_size` determines how many boxes will the 24-bit color space be
    devided into. The larger `box_size`, the less boxes will there be.

    `box_size` should not be too large or too small, or the optimization will
    not really work.

    The result can be indexed by [(r<<16) + (g<<8) + b]
    """
    def color_distance(i:int) -> float:
        """
        return the distance between `palette[i]` and `(r, g, b)`
        """
        return dist(palette[i], (r, g, b))
    
    def add_neighbor_boxes(
            i:int, 
            box_side_count:int, 
            current_box_coord:tuple[int, int, int], 
            palette_boxes:dict[tuple[int, int, int], list[int]],
            colors_to_test:list[int], 
    ) -> None:
        R_LEFT = 0 if current_box_coord[0] - i <= 0 else current_box_coord[0] - i
        R_RIGHT = box_side_count if current_box_coord[0] + i > box_side_count else current_box_coord[0] + i
        G_LEFT = 0 if current_box_coord[1] - i <= 0 else current_box_coord[1] - i
        G_RIGHT = box_side_count if current_box_coord[1] + i > box_side_count else current_box_coord[1] + i
        B_LEFT = 0 if current_box_coord[2] - i <= 0 else current_box_coord[2] - i
        B_RIGHT = box_side_count if current_box_coord[2] + i > box_side_count else current_box_coord[2] + i
        # Top and bottom surface
        for g in range(G_LEFT, G_RIGHT + 1):
            for r in range(R_LEFT, R_RIGHT + 1):
                if (r, g, B_LEFT) in palette_boxes.keys():
                    colors_to_test.extend(palette_boxes[(r, g, B_LEFT)])
                if (r, g, B_RIGHT) in palette_boxes.keys():
                    colors_to_test.extend(palette_boxes[(r, g, B_RIGHT)])
        # Sides, [B_LEFT + 1, B_RIGHT - 1]
        for b in range(B_LEFT + 1, B_RIGHT):
            for g in range(G_LEFT, G_RIGHT + 1):
                if (R_LEFT, g, b) in palette_boxes.keys():
                        colors_to_test.extend(palette_boxes[(R_LEFT, g, b)])
                if (R_RIGHT, g, b) in palette_boxes.keys():
                        colors_to_test.extend(palette_boxes[(R_RIGHT, g, b)])
            # Corners have been taken cared of above, so [R_LEFT + 1, R_RIGHT - 1]
            for r in range(R_LEFT + 1, R_RIGHT):
                if (r, G_LEFT, b) in palette_boxes.keys():
                        colors_to_test.extend(palette_boxes[(r, G_LEFT, b)])
                if (r, G_RIGHT, b) in palette_boxes.keys():
                        colors_to_test.extend(palette_boxes[(r, G_RIGHT, b)])

    if len(palette) > 256:
        raise ValueError(f"`palette` size cannot exceed 256. "
                         f"Got ..., {str(palette[-5:])[1:-1]}"
                         f" of length {len(palette)}")
    
    palette_boxes:dict[tuple[int, int, int], list[int]] = {}
    # Map palette colors to 24-bit
    palette = tuple(
        (round(color.r * 255.0) // box_size, 
         round(color.g * 255.0) // box_size, 
         round(color.b * 255.0) // box_size)
        for color in palette
    )
    for i, color in enumerate(palette):
        box_coord = (round(color.r * 255.0) // box_size, 
                     round(color.g * 255.0) // box_size, 
                     round(color.b * 255.0) // box_size)
        if box_coord not in palette_boxes.keys():
            palette_boxes[box_coord] = [i]
        else:
            palette_boxes[box_coord].append(i)

    box_side_count = ceil(256 / box_size)

    out = bytearray(1<<24)

    for r in range(256):
        for g in range(256):
            process_bar(g + (r << 8), 1 << 16, progress_bar_width)
            for b in range(256):
                box_coord = (r // box_size, g // box_size, b // box_size)
                colors_to_test = []
                # The box the color itself is in
                if box_coord in palette_boxes.keys():
                    colors_to_test.extend(palette_boxes[box_coord])
                # Neighboring boxes 
                # Increase the search range `i` if nothing is found
                for i in range(1, box_side_count):
                    add_neighbor_boxes(i, box_side_count, box_coord, palette_boxes, colors_to_test)
                    if len(colors_to_test) > 0:
                        break

                out[(r << 16) + (g << 8) + b] = min(colors_to_test, 
                                                    key=color_distance)
    return out
