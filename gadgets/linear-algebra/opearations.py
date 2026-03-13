from __future__ import annotations

from timeit import timeit
from random import seed

from matrix4d import Matrix4d, Matrix4dTuple
from vec4d import Vec4d, Vector4dTuple


def mat4t_mul_(m1: Matrix4dTuple, m2: Matrix4dTuple) -> Matrix4dTuple:
    return (
        m1[0] * m2[0] + m1[1] * m2[4] + m1[2] * m2[8] + m1[3] * m2[12],
        m1[0] * m2[1] + m1[1] * m2[5] + m1[2] * m2[9] + m1[3] * m2[13],
        m1[0] * m2[2] + m1[1] * m2[6] + m1[2] * m2[10]+ m1[3] * m2[14],
        m1[0] * m2[3] + m1[1] * m2[7] + m1[2] * m2[11]+ m1[3] * m2[15],
        
        m1[4] * m2[0] + m1[5] * m2[4] + m1[6] * m2[8] + m1[7] * m2[12],
        m1[4] * m2[1] + m1[5] * m2[5] + m1[6] * m2[9] + m1[7] * m2[13],
        m1[4] * m2[2] + m1[5] * m2[6] + m1[6] * m2[10]+ m1[7] * m2[14],
        m1[4] * m2[3] + m1[5] * m2[7] + m1[6] * m2[11]+ m1[7] * m2[15],
        
        m1[8] * m2[0] + m1[9] * m2[4] + m1[10]* m2[8] + m1[11]* m2[12],
        m1[8] * m2[1] + m1[9] * m2[5] + m1[10]* m2[9] + m1[11]* m2[13],
        m1[8] * m2[2] + m1[9] * m2[6] + m1[10]* m2[10]+ m1[11]* m2[14],
        m1[8] * m2[3] + m1[9] * m2[7] + m1[10]* m2[11]+ m1[11]* m2[15],
        
        m1[12]* m2[0] + m1[13]* m2[4] + m1[14]* m2[8] + m1[15]* m2[12],
        m1[12]* m2[1] + m1[13]* m2[5] + m1[14]* m2[9] + m1[15]* m2[13],
        m1[12]* m2[2] + m1[13]* m2[6] + m1[14]* m2[10]+ m1[15]* m2[14],
        m1[12]* m2[3] + m1[13]* m2[7] + m1[14]* m2[11]+ m1[15]* m2[15],
    )

def mat4t_mul__(m1: Matrix4dTuple, m2: Matrix4dTuple) -> Matrix4dTuple:
    (a00, a01, a02, a03,
     a10, a11, a12, a13,
     a20, a21, a22, a23,
     a30, a31, a32, a33) = m1
    (b00, b01, b02, b03,
     b10, b11, b12, b13,
     b20, b21, b22, b23,
     b30, b31, b32, b33) = m2
    return (
        a00 * b00 + a01 * b10 + a02 * b20 + a03 * b30,
        a00 * b01 + a01 * b11 + a02 * b21 + a03 * b31,
        a00 * b02 + a01 * b12 + a02 * b22 + a03 * b32,
        a00 * b03 + a01 * b13 + a02 * b23 + a03 * b33,
        
        a10 * b00 + a11 * b10 + a12 * b20 + a13 * b30,
        a10 * b01 + a11 * b11 + a12 * b21 + a13 * b31,
        a10 * b02 + a11 * b12 + a12 * b22 + a13 * b32,
        a10 * b03 + a11 * b13 + a12 * b23 + a13 * b33,
        
        a20 * b00 + a21 * b10 + a22 * b20 + a23 * b30,
        a20 * b01 + a21 * b11 + a22 * b21 + a23 * b31,
        a20 * b02 + a21 * b12 + a22 * b22 + a23 * b32,
        a20 * b03 + a21 * b13 + a22 * b23 + a23 * b33,
        
        a30 * b00 + a31 * b10 + a32 * b20 + a33 * b30,
        a30 * b01 + a31 * b11 + a32 * b21 + a33 * b31,
        a30 * b02 + a31 * b12 + a32 * b22 + a33 * b32,
        a30 * b03 + a31 * b13 + a32 * b23 + a33 * b33,
    )

def mat4t_mul___(
    a00: float, a01: float, a02: float, a03: float,
    a10: float, a11: float, a12: float, a13: float,
    a20: float, a21: float, a22: float, a23: float,
    a30: float, a31: float, a32: float, a33: float,
     
    b00: float, b01: float, b02: float, b03: float,
    b10: float, b11: float, b12: float, b13: float,
    b20: float, b21: float, b22: float, b23: float,
    b30: float, b31: float, b32: float, b33: float,
) -> Matrix4dTuple:
    return (
        a00 * b00 + a01 * b10 + a02 * b20 + a03 * b30,
        a00 * b01 + a01 * b11 + a02 * b21 + a03 * b31,
        a00 * b02 + a01 * b12 + a02 * b22 + a03 * b32,
        a00 * b03 + a01 * b13 + a02 * b23 + a03 * b33,
        
        a10 * b00 + a11 * b10 + a12 * b20 + a13 * b30,
        a10 * b01 + a11 * b11 + a12 * b21 + a13 * b31,
        a10 * b02 + a11 * b12 + a12 * b22 + a13 * b32,
        a10 * b03 + a11 * b13 + a12 * b23 + a13 * b33,
        
        a20 * b00 + a21 * b10 + a22 * b20 + a23 * b30,
        a20 * b01 + a21 * b11 + a22 * b21 + a23 * b31,
        a20 * b02 + a21 * b12 + a22 * b22 + a23 * b32,
        a20 * b03 + a21 * b13 + a22 * b23 + a23 * b33,
        
        a30 * b00 + a31 * b10 + a32 * b20 + a33 * b30,
        a30 * b01 + a31 * b11 + a32 * b21 + a33 * b31,
        a30 * b02 + a31 * b12 + a32 * b22 + a33 * b32,
        a30 * b03 + a31 * b13 + a32 * b23 + a33 * b33,
    )
    
    
    
def mat4t_mul_vec4t_(m: Matrix4dTuple, v: Vector4dTuple) -> Vector4dTuple:
    (m00, m01, m02, m03,
     m10, m11, m12, m13,
     m20, m21, m22, m23,
     m30, m31, m32, m33) = m
    v0, v1, v2, v3 = v
    return (
        m00 * v0 + m01 * v1 + m02 * v2 + m03 * v3,
        m10 * v0 + m11 * v1 + m12 * v2 + m13 * v3,
        m20 * v0 + m21 * v1 + m22 * v2 + m23 * v3,
        m30 * v0 + m31 * v1 + m32 * v2 + m33 * v3,
    )

def mat4t_mul_vec4t__(m: Matrix4dTuple, v: Vector4dTuple) -> Vector4dTuple:
    v0, v1, v2, v3 = v
    return (
        m[0] * v0 + m[1] * v1 + m[2] * v2 + m[3] * v3,
        m[4] * v0 + m[5] * v1 + m[6] * v2 + m[7] * v3,
        m[8] * v0 + m[9] * v1 + m[10] * v2 + m[11] * v3,
        m[12] * v0 + m[13] * v1 + m[14] * v2 + m[15] * v3,
    )
    
    
    
def mat4t_add_(a: Matrix4dTuple, b: Matrix4dTuple) -> Matrix4dTuple:
    # The static type checker is not smart enough to deduce the length
    return tuple(x + y for x, y in zip(a, b)) # type: ignore

def mat4t_add__(a: Matrix4dTuple, b: Matrix4dTuple) -> Matrix4dTuple:
    (a00, a01, a02, a03,
     a10, a11, a12, a13,
     a20, a21, a22, a23,
     a30, a31, a32, a33) = a
    (b00, b01, b02, b03,
     b10, b11, b12, b13,
     b20, b21, b22, b23,
     b30, b31, b32, b33) = b
    return (
        a00 + b00, a01 + b01, a02 + b02, a03 + b03,
        a10 + b10, a11 + b11, a12 + b12, a13 + b13,
        a20 + b20, a21 + b21, a22 + b22, a23 + b23,
        a30 + b30, a31 + b31, a32 + b32, a33 + b33,
    )
    
mat4t_mul = mat4t_mul__
mat4t_mul_vec4t = mat4t_mul_vec4t_
mat4t_add_ = mat4t_add__

if 0:
    seed(0)
    for _ in range(1000):
        m1 = Matrix4d.random().to_tuple()
        m2 = Matrix4d.random().to_tuple()
        r1 = mat4t_mul_(m1, m2)
        r2 = mat4t_mul__(m1, m2)
        r3 = mat4t_mul___(*m1, *m2)
        assert Matrix4d(*r1).to_string() == Matrix4d(*r2).to_string()
        assert Matrix4d(*r1).to_string() == Matrix4d(*r3).to_string()

if 0:
    seed(0)
    m1 = Matrix4d.random().to_tuple()
    m2 = Matrix4d.random().to_tuple()
    print(timeit(
        "mat4t_mul(m1, m2)",
        setup="from __main__ import mat4t_mul_, m1, m2",
        number=10**6,
    ))
    print(timeit(
        "mat4t_mul_(m1, m2)",
        setup="from __main__ import mat4t_mul__, m1, m2",
        number=10**6,
    ))
    print(timeit(
        "mat4t_mul__(*m1, *m2)",
        setup="from __main__ import mat4t_mul___, m1, m2",
        number=10**6,
    ))

if 0:
    seed(0)
    m = Matrix4d.random().to_tuple()
    v = Vec4d.random().to_tuple()
    print(timeit(
        "mat4t_mul_vec4t_(m, v)",
        setup="from __main__ import mat4t_mul_vec4t_, m, v",
        number=4*10**6,
    ))
    print(timeit(
        "mat4t_mul_vec4t__(m, v)",
        setup="from __main__ import mat4t_mul_vec4t__, m, v",
        number=4*10**6,
    ))

if 1:
    seed(0)
    m1 = Matrix4d.random().to_tuple()
    m2 = Matrix4d.random().to_tuple()
    print(timeit(
        "mat4t_add_(m1, m2)",
        setup="from __main__ import mat4t_add_, m1, m2",
        number=4*10**6,
    ))
    print(timeit(
        "mat4t_add__(m1, m2)",
        setup="from __main__ import mat4t_add__, m1, m2",
        number=4*10**6,
    ))
