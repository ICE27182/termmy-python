# termmy
termmy is a pure python library that provide APIs for GUI in the terminals.
It aims for minimal overhead and maximum cross-platform compatibility.
Note that being a pure python library that runs in a terminal, 
it inevitably has considerable overhead comparing to a industry-standard GUI library.
It also has limited support for input depending on platforms.

It is mainly for fun and learning purposes.

## Major Features

### display
This function displays Buffer2D instances to the terminal.

### ColorBuffer
- Provide pixel-level control over the output of the terminal.

### Scene
- Allows for usages of nodes.

### Image
- Supports image decoding/encoding.

### Text
- Supports text rendering with typography.

### TermIOHub
- Reads keyboard inputs, interpret control sequence if possible. 
- Records and replays keyboard input.
- Provide context in which default IO behaviors are preserved 
  while keyboard is being read.

## 
In order to mitigate the overhead, it is recommended to operate on the 
attributes directly instead of using equivlent methods where performance is of
concern.
