

from .color import Color
from termmy.core import process_bar

from collections.abc import Iterable
from math import ceil, dist, log2

DEFAULT_ALPHA:int = 255

def _add_neighboring_boxes(
    radius:int, 
    box_num_per_dim:int, 
    current_box_coord:tuple[int, int, int], 
    palette_boxes:dict[tuple[int, int, int], list[int]],
    candidate_colors:list[int], 
) -> None:
    """
    Add neighboring boxes to `candidate_colors` list
    """
    current_box_r, current_box_g, current_box_b = current_box_coord
    R_LEFT = 0 if current_box_r - radius <= 0 else current_box_r - radius
    R_RIGHT = (box_num_per_dim if current_box_r + radius > box_num_per_dim 
               else current_box_r + radius)
    G_LEFT = 0 if current_box_g - radius <= 0 else current_box_g - radius
    G_RIGHT = (box_num_per_dim if current_box_g + radius > box_num_per_dim 
               else current_box_g + radius)
    B_LEFT = 0 if current_box_b - radius <= 0 else current_box_b - radius
    B_RIGHT = (box_num_per_dim if current_box_b + radius > box_num_per_dim 
               else current_box_b + radius)
    # Top and bottom surface
    for g in range(G_LEFT, G_RIGHT + 1):
        for r in range(R_LEFT, R_RIGHT + 1):
            if (r, g, B_LEFT) in palette_boxes.keys():
                candidate_colors.extend(palette_boxes[(r, g, B_LEFT)])
            if (r, g, B_RIGHT) in palette_boxes.keys():
                candidate_colors.extend(palette_boxes[(r, g, B_RIGHT)])
    # Sides, [B_LEFT + 1, B_RIGHT - 1]
    for b in range(B_LEFT + 1, B_RIGHT):
        for g in range(G_LEFT, G_RIGHT + 1):
            if (R_LEFT, g, b) in palette_boxes.keys():
                    candidate_colors.extend(palette_boxes[(R_LEFT, g, b)])
            if (R_RIGHT, g, b) in palette_boxes.keys():
                    candidate_colors.extend(palette_boxes[(R_RIGHT, g, b)])
        # Corners have been taken cared of above, so [R_LEFT + 1, R_RIGHT - 1]
        for r in range(R_LEFT + 1, R_RIGHT):
            if (r, G_LEFT, b) in palette_boxes.keys():
                    candidate_colors.extend(palette_boxes[(r, G_LEFT, b)])
            if (r, G_RIGHT, b) in palette_boxes.keys():
                    candidate_colors.extend(palette_boxes[(r, G_RIGHT, b)])


# color quantization with brute force
def get_color_quantization_table(palette:Iterable[Color], 
                                 box_size:int = 32, 
                                 progress_bar:None|int=20) -> bytearray:
    """
    Use brute force to find the color in the palette for all 24bit colors
    (the result will be 3MB)

    Length of `palette` must not exceed 256 because we are using bytes to
    store the result and 8-bit integers are used to index the palette

    `box_size` must be a power of 2. It determines how many boxes will 
    the 24-bit color space be devided into. The larger `box_size`, the 
    less boxes will there be.

    `box_size` should not be too large or too small, or the optimization will
    not really work.

    The result can be indexed by [(r<<16) + (g<<8) + b]
    """
    def color_distance(i:int) -> float:
        """
        return the distance between `palette[i]` and `(r, g, b)`
        """
        return dist(palette[i], (r, g, b))
    
    if len(palette) > 256:
        raise ValueError(f"`palette` size cannot exceed 256. "
                         f"Got ..., {str(palette[-5:])[1:-1]}"
                         f" of length {len(palette)}")
    log2_box_size = log2(box_size)
    if log2_box_size != int(log2_box_size):
        raise ValueError("`box_size` must be a power of 2."
                         f"Got {box_size}.")
    log2_box_size = int(log2_box_size)
    
    # Map palette colors to 24-bit
    palette = tuple(
        (round(color.r * 255.0), 
         round(color.g * 255.0), 
         round(color.b * 255.0))
        for color in palette
    )
    # Group palette colors into different boxes
    palette_boxes:dict[tuple[int, int, int], list[int]] = {}
    for index, color in enumerate(palette):
        box_coord = (color[0] >> log2_box_size, 
                     color[1] >> log2_box_size, 
                     color[2] >> log2_box_size)
        if box_coord not in palette_boxes.keys():
            palette_boxes[box_coord] = [index]
        else:
            palette_boxes[box_coord].append(index)

    box_num_per_dim = ceil(256 / log2_box_size)

    out = bytearray(1<<24)

    for r in range(0, 256):
        for g in range(0, 256):
            process_bar(g + (r << 8), 1 << 16, progress_bar)
            for b in range(0, 256):
                box_coord = (r >> log2_box_size, g >> log2_box_size, b >> log2_box_size)
                candidate_colors = []
                # The box the color itself is in
                if box_coord in palette_boxes.keys():
                    candidate_colors.extend(palette_boxes[box_coord])
                # Search among neighboring boxes 
                # The searching range `radius` will increment if nothing
                # has been found.
                for radius in range(1, box_num_per_dim):
                    _add_neighboring_boxes(radius, box_num_per_dim, box_coord,
                                           palette_boxes, candidate_colors)
                    if len(candidate_colors) > 0:
                        break
                out[(r << 16) + (g << 8) + b] = min(candidate_colors, 
                                                    key=color_distance)
    return out

