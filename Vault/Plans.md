# Plans

## v 1

A working system where translucent geometries with geometry based z

A 2D universe simulation

### Features

- **Rendering Objects**
  - 2D
  - Translucency
  - Objec  -level z value
  - Texture & UV mapping (modulus based wrapping)
  - Transform (Scale, Offset, Rotation) & Center
  - Listener

- **Rendering Targets**
  - Color Buffer

- **IO**
  - Full keyboard, mouse input support
  - Displaying the color buffer (normal / super resolution)

- **Images**

  - BMP

### Compromises

- **Rendering Objects**
  - Text (Rendered/Embedded)
  - Optional Translucency for performance
  - No inlining (It is also less relevant in this version because there are less cases due to the limited features. Using inlining in the current version is more like the micro-optimization)
