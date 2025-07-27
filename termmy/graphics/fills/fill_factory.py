


from .fills import SolidFill, LinearFill
from ...colors import Color
from ...core import UV

class FillFactory:
    @staticmethod
    def get_solid_fill(color: Color) -> SolidFill:
        return SolidFill(Color(color.r, color.g, color.b, color.a))
    
    @staticmethod
    def get_linear_fill(color1: Color, color2: Color, *args) -> LinearFill:
        """Returns a linear fill object with even stops. The colors will
        be stored as references.
        """
        interval_num_inv = 1 / (1 + len(args))
        stops = [(0.0, color1), (interval_num_inv, color2)]
        stops.extend(((i * interval_num_inv, color) 
                      for i, color in enumerate(args, 2)))
        return LinearFill(stops)
