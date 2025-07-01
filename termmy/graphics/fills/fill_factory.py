


from .fill import Fill
from .fills import SolidFill
from ...colors import Color

class FillFactory:
    @staticmethod
    def get_solid_fill(color: Color) -> Fill:
        return SolidFill(Color(color.r, color.g, color.b, color.a))
