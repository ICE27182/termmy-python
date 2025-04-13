# termmy
termmy is a pure python library that provide APIs for GUI in the terminals.

## Major Features

### display
This function displays Buffer2D instances to the terminal.

### Buffer2D
An abstract class that can be inherited from for 2 dimensional buffers 
like color buffers, normal buffers, depth buffers, etc.
#### ColorBuffer
A class inheriting from Buffer2D for 2 dimensional image representation. Supports
high precision RGBA information storage.

### Image
Supports image decoding/encoding. 
Compositioned a ColorBuffer internally for data storage.

### Text
Supports normal terminal text (Overlay only) 
and text rendering to a Buffer2D object.
(Partially) supports different typography.

### Overlay
Stores overlaid text and geometries on top of the buffer to be displayed.

### TermHub
Reads keyboard inputs, interpret control sequence if possible. 
Records and replays keyboard input.
Provide print and input 
(Default print and input may not work properly due to the need of keyboard reading)
