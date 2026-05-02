"""
Copied and pasted from gadgets/linear-algebra/linear_algebra.py
"""


from math import sin, cos

Matrix4dTuple = tuple[float, float, float, float,
                      float, float, float, float,
                      float, float, float, float,
                      float, float, float, float]
Vector4dTuple = tuple[float, float, float, float]

###############################################################
#
# Arithmetic
#
###############################################################

###############################################################
# Multiplication
###############################################################

def mat4t_mul(m1: Matrix4dTuple, m2: Matrix4dTuple) -> Matrix4dTuple:
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


def mat4t_mul_vec4t(m: Matrix4dTuple, v: Vector4dTuple) -> Vector4dTuple:
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


def mat4t_add(a: Matrix4dTuple, b: Matrix4dTuple) -> Matrix4dTuple:
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
    

###############################################################
# Inverse
###############################################################

def mat4t_orthogonal_inverse(m: Matrix4dTuple) -> Matrix4dTuple:
    (m00, m01, m02, v0,
     m10, m11, m12, v1,
     m20, m21, m22, v2,
     _, _, _, _) = m
    return (
        m00, m10, m20, -(m00 * v0 + m10 * v1 + m20 * v2),
        m01, m11, m21, -(m01 * v0 + m11 * v1 + m21 * v2),
        m02, m12, m22, -(m02 * v0 + m12 * v1 + m22 * v2),
        0.0, 0.0, 0.0, 1.0,
    )


def mat4t_inverse(m: Matrix4dTuple) -> Matrix4dTuple:
    (m00, m01, m02, m03,
     m10, m11, m12, m13,
     m20, m21, m22, m23,
     m30, m31, m32, m33) = m

    s0 = m00 * m11 - m01 * m10
    s1 = m00 * m12 - m02 * m10
    s2 = m00 * m13 - m03 * m10
    s3 = m01 * m12 - m02 * m11
    s4 = m01 * m13 - m03 * m11
    s5 = m02 * m13 - m03 * m12

    c0 = m20 * m31 - m21 * m30
    c1 = m20 * m32 - m22 * m30
    c2 = m20 * m33 - m23 * m30
    c3 = m21 * m32 - m22 * m31
    c4 = m21 * m33 - m23 * m31
    c5 = m22 * m33 - m23 * m32

    det = s0 * c5 - s1 * c4 + s2 * c3 + s3 * c2 - s4 * c1 + s5 * c0
    if det == 0.0:
        raise ValueError("Matrix is singular and cannot be inverted.")

    inv00 = m11 * c5 - m12 * c4 + m13 * c3
    inv01 = -m01 * c5 + m02 * c4 - m03 * c3
    inv02 = m31 * s5 - m32 * s4 + m33 * s3
    inv03 = -m21 * s5 + m22 * s4 - m23 * s3

    inv10 = -m10 * c5 + m12 * c2 - m13 * c1
    inv11 = m00 * c5 - m02 * c2 + m03 * c1
    inv12 = -m30 * s5 + m32 * s2 - m33 * s1
    inv13 = m20 * s5 - m22 * s2 + m23 * s1

    inv20 = m10 * c4 - m11 * c2 + m13 * c0
    inv21 = -m00 * c4 + m01 * c2 - m03 * c0
    inv22 = m30 * s4 - m31 * s2 + m33 * s0
    inv23 = -m20 * s4 + m21 * s2 - m23 * s0

    inv30 = -m10 * c3 + m11 * c1 - m12 * c0
    inv31 = m00 * c3 - m01 * c1 + m02 * c0
    inv32 = -m30 * s3 + m31 * s1 - m32 * s0
    inv33 = m20 * s3 - m21 * s1 + m22 * s0

    inv_det = 1.0 / det
    return (
        inv00 * inv_det, inv01 * inv_det, inv02 * inv_det, inv03 * inv_det,
        inv10 * inv_det, inv11 * inv_det, inv12 * inv_det, inv13 * inv_det,
        inv20 * inv_det, inv21 * inv_det, inv22 * inv_det, inv23 * inv_det,
        inv30 * inv_det, inv31 * inv_det, inv32 * inv_det, inv33 * inv_det,
    )
    
###############################################################
#
# Constructors
#
###############################################################

###############################################################
# Rotation
###############################################################

def rot_mat_x(rad: float) -> Matrix4dTuple:
    s = sin(rad)
    c = cos(rad)
    return (
        1.0, 0.0, 0.0, 0.0,
        0.0, c, -s, 0.0,
        0.0, s, c, 0.0,
        0.0, 0.0, 0.0, 1.0,
    )


def rot_mat_y(rad: float) -> Matrix4dTuple:
    s = sin(rad)
    c = cos(rad)
    return (
        c, 0.0, s, 0.0,
        0.0, 1.0, 0.0, 0.0,
        -s, 0.0, c, 0.0,
        0.0, 0.0, 0.0, 1.0,
    )


def rot_mat_z(rad: float) -> Matrix4dTuple:
    s = sin(rad)
    c = cos(rad)
    return (
        c, -s, 0.0, 0.0,
        s, c, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0,
    )

###############################################################
# Translation
###############################################################

def translation(v: Vector4dTuple) -> Matrix4dTuple:
    v0, v1, v2, v3 = v
    return (
        1.0, 0.0, 0.0, v0,
        0.0, 1.0, 0.0, v1,
        0.0, 0.0, 1.0, v2,
        0.0, 0.0, 0.0, v3,
    )
    
###############################################################
# Scaling
###############################################################

def scaling(v: Vector4dTuple) -> Matrix4dTuple:
    v0, v1, v2, v3 = v
    return (
        v0, 0.0, 0.0, 0.0,
        0.0, v1, 0.0, 0.0,
        0.0, 0.0, v2, 0.0,
        0.0, 0.0, 0.0, v3,
    )
    
###############################################################
# Identity
###############################################################

def identity_mat4t() -> Matrix4dTuple:
    return (
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0,
    )

def add_translation_to_mat4t(v: Vector4dTuple, m: Matrix4dTuple) -> Matrix4dTuple:
    v0, v1, v2, _ = v
    (m00, m01, m02, m03,
     m10, m11, m12, m13,
     m20, m21, m22, m23,
     m30, m31, m32, m33) = m
    return (
        m00, m01, m02, m03 + v0,
        m10, m11, m12, m13 + v1,
        m20, m21, m22, m23 + v2,
        m30, m31, m32, m33,
    )


