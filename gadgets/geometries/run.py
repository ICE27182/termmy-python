from time import sleep
from math import radians

from basics import render, Buffer, Color, Transform
from linear_algebra import *
from geometry_rectangle import Rectangle
from geometry_circle import Circle, CircleUVRadialLinear
from geometry_line import Line


b = Buffer.empty(120, 56, 255, 255, 255)

circ = Circle.create(60, 30, 25, Color(0, 0, 0xFF, 0x80))
circ.transform.mat4 = circ.transform.mat4

g = [circ]

i = 0
p = 24

n = 3
while True:
    n = abs(i // 6 % (p - 3) - p // 2) + 3
    circ.set_vertex_num(n)
    
    mat4 = circ.transform.mat4
    circ.transform.mat4 = mat4t_mul(circ.transform.mat4, 
                                    mat4t_mul(rot_mat_z(radians(i * 3)),
                                              Transform.scaling(1.5, 0.8, 1.0).mat4))
    render(g, b)
    circ.transform.mat4 = mat4
    
    b.show()
    print(n, 1 // circ._vertex_num_reciprocal, end='\r')
    b.fill(0xff, 0xff, 0xff)
    sleep(1 / 60)
    # input()

    i += 1
