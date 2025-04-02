

from .constants import DEFAULT_ALPHA, BOX_SIZE
from .core.progress_bar import process_bar
from .type_aliases import Pixel, RGB

from math import ceil, dist



# color quantization with brute force
def get_color_quantization_table(palette:list[RGB], 
                                 box_size:int = BOX_SIZE, 
                                 progress_bar_width:None|int=20) -> bytearray:
    """
    Use brute force to find the color in the palette for all 24bit colors
    (the result will be LARGE)

    Length of `palette` must not exceed 256 because we are using bytes to
    store the result, so 8-bit integers to index the palette

    `box_size` determines how many boxes will the 24-bit color space be
    devided into. The larger `box_size`, the less boxes will there be.

    `box count = ceil(255 / box_size)^3`

    `box_size` should not be too large or too small, or the optimization will
    not really work.
    """
    def color_distance(i:int) -> float:
        """
        return the distance between `palette[i]` and `(r, g, b)`
        """
        return dist(palette[i], (r, g, b))
    
    def check_neighbor_boxes(
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
                         f"Got [..., {str(palette[-5:])[1:-1]}]"
                         f" of length {len(palette)}")
    
    palette_boxes:dict[tuple[int, int, int], list[int]] = {}
    for i, color in enumerate(palette):
        box_coord = (color[0] // box_size, color[1] // box_size, color[2] // box_size)
        if box_coord not in palette_boxes.keys():
            palette_boxes[box_coord] = [i]
        else:
            palette_boxes[box_coord].append(i)

    box_side_count = ceil(256 / box_size)

    out = bytearray(256**3)

    for b in range(256):
        for g in range(256):
            process_bar(g + (b << 8), 1 << 16, progress_bar_width)
            for r in range(256):
                box_coord = (r // box_size, g // box_size, b // box_size)
                colors_to_test = []
                # The box the color itself is in
                if box_coord in palette_boxes.keys():
                    colors_to_test.extend(palette_boxes[box_coord])
                # Neighboring boxes 
                # Increase the search range `i` if nothing is found
                for i in range(1, box_side_count):
                    check_neighbor_boxes(i, box_side_count, box_coord, palette_boxes, colors_to_test)
                    if len(colors_to_test) > 0:
                        break

                out[r + (g << 8) + (b << 16)] = min(colors_to_test, 
                                                    key=color_distance)
    return out



def compose_alpha(old:Pixel, new:Pixel) -> RGB:
    """
        Discard the alpha of `old` and merge the new pixel with its alpha.
        The new pixel does not have alpha, `cconstants.DEFAULT_ALPHA` will be
        used.
    """
    if len(new) != 4:
        alpha = DEFAULT_ALPHA / 255
    else:
        alpha = new[3] / 255
    complement_alpha = 1 - alpha
    return (
        int(old[0] * complement_alpha + new[0] * alpha),
        int(old[1] * complement_alpha + new[1] * alpha),
        int(old[2] * complement_alpha + new[2] * alpha),
    )

def get_grayscale(pixel:Pixel) -> int:
    return int(0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2])

def rgb_to_ansi8_str():
    pass
    