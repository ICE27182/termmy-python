from dataclasses import dataclass

@dataclass(slots=True)
class AntiAliasingSettings:
    fxaa: bool = False
    fxaa_threshold: float = 0.125
    msaa_level: int = 0
    msaa_pattern: tuple[tuple[float, float], ...] = tuple()
    aaa_level: int = 0
    aaa_pattern: tuple[tuple[float, float], ...] = tuple()
    ssaa_level: int = 0
