

from __future__ import annotations

from typing import Self, Final, overload
from collections.abc import Iterable
from numbers import Number

class Matrix:
    _data: list[Number]
    _dimension: Final[int]

    def __init__(self, dimesion: int, data: list[Number] = None):
        self._data = data or [[0] * dimesion for _ in range(dimesion)]
        self._dimension = dimesion
    
    @staticmethod
    def get_identity_matrix(dimesion: int) -> Matrix:
        data = ([1.0] + [0.0] * dimesion) * (dimesion - 1) + [1.0]
        return Matrix(dimesion, data)
    

    def __str__(self) -> str:
        PRECISION = 3
        out = []
        data = tuple(map(lambda f:f"{f:.{PRECISION}f}", self._data))
        dim = self._dimension
        max_digit = max(map(len, data))
        for y in range(dim):
            for x in range(dim):
                out.append(f"{data[y * dim + x]:<{max_digit + 3}}")
            out.append("\n")
        return "".join(out).replace(f"-{0:.{PRECISION}f}", 
                                    f"{0:.{PRECISION}f} ")
    
    def __eq__(self, mat: Self) -> bool:
        return self._dimension == mat._dimension and self._data == mat._data
    
    def __getitem__(self, position: tuple[int, int]) -> Number:
        return self._data[position[0] * self._dimension + position[1]]
    
    def __setitem__(self, position: tuple[int, int], value: Number) -> None:
        self._data[position[0] * self._dimension + position[1]] = value
    
    @overload
    def __mul__(self, other: Number) -> Matrix: ...
    @overload
    def __mul__(self, other: Iterable[Number]) -> tuple[Number]: ...
    @overload
    def __mul__(self, other: Matrix) -> Matrix: ...
    
    def __mul__(self, other: Iterable[Number] 
                             | Number 
                             | Matrix) -> Iterable[Number] | Matrix:
        if isinstance(other, Matrix):
            return self.mul_mat(other)
        elif isinstance(other, Iterable):
            return self.mul_vec(other)
        elif isinstance(other, Number):
            return self.mul_num(other)
        else:
            raise ValueError("Unsupported operand type(s) "
                             f"for: {type(other)}")
    

    def get_transposed(self) -> Matrix:
        dim = self._dimension
        return Matrix(
            dim, 
            [
                self._data[j * dim + i] 
                for i in range(dim)
                    for j in range(dim)
            ],
        )

    def get_inverse(self) -> Matrix | None:
        """
        Get the inverse with Gaussian Elimination

        Returns `None` if the inverse does not exist
        """
        dim = self._dimension
        mat = Matrix(dim, self._data[:])
        inverse:Matrix = Matrix.get_identity_matrix(dim)
        # Make all pivots 1
        for pivot_no in range(dim):
            for row_no in range(pivot_no, dim):
                if mat[row_no, pivot_no] != 0:
                    mat._swap_row(pivot_no, row_no)
                    inverse._swap_row(pivot_no, row_no)
                    break
            else:
                return None
            multiplicator = 1 / mat[pivot_no, pivot_no]
            inverse._mul_row(pivot_no, multiplicator)
            mat._mul_row(pivot_no, multiplicator)
            for row_no in range(pivot_no + 1, dim):
                multiplicator = mat[row_no, pivot_no]
                mat._sub_multiples_of_row(row_no, pivot_no, multiplicator)
                inverse._sub_multiples_of_row(row_no, pivot_no, multiplicator)
        # Make non pivots 0
        # `dim - 1` iterations excluding last row
        for pivot_no in range(dim - 2, -1, -1):
            for col_no in range(pivot_no + 1, dim):
                inverse._sub_multiples_of_row(pivot_no, col_no, mat[pivot_no, col_no])
        return inverse

    def mul_vec(self, vector: Iterable[Number]) -> tuple:
        dim = self._dimension
        if len(vector) != dim:
            raise ValueError("Invalid dimension")
        return tuple(
            sum(v * u 
                for v, u in zip(
                    vector, 
                    self._data[row_starting:row_starting + dim],
                )
            ) 
            for row_starting in range(0, len(self._data), dim)
        )

    def mul_mat(self, matrix: Self) -> Matrix:
        dim = self._dimension
        dim_squared = len(self._data)
        if matrix._dimension != dim:
            raise ValueError("Invalid dimension")
        matrix_T = matrix.get_transposed()
        return Matrix(
            dim,
            [
                sum(
                    v * u
                    for v, u in zip(
                        self._data[row1_starting:row1_starting + dim],
                        matrix_T._data[row2_starting:row2_starting + dim], 
                    )
                )
                for row1_starting in range(0, dim_squared, dim)
                for row2_starting in range(0, dim_squared, dim)
            ]
        )
    
    def mul_num(self, number: Number) -> Matrix:
        return Matrix(
            self._dimension,
            [number * value for value in self._data]
        )


    def _swap_row(self, row1_no: int, row2_no: int) -> None:
        dim, data = self._dimension, self._data
        row1_starting = row1_no * dim
        row2_starting = row2_no * dim
        for col_no in range(dim):
            # Swap elements between the two rows
            (data[row1_starting + col_no], 
             data[row2_starting + col_no]) = (data[row2_starting + col_no],
                                              data[row1_starting + col_no])
    
    def _mul_row(self, row_no: int, multiplicator: Number) -> None:
        dim, data = self._dimension, self._data
        row_starting = row_no * dim
        for col_no in range(dim):
            data[row_starting + col_no] *= multiplicator
    
    def _sub_multiples_of_row(
        self, 
        minuend_row_no: int, 
        substrachend_row_no: int, 
        multiplicator: Number
    ) -> None:
        dim, data = self._dimension, self._data
        minu_starting = minuend_row_no * dim
        subs_starting = substrachend_row_no * dim
        for col_no in range(dim):
            data[minu_starting + col_no] -= (data[subs_starting + col_no]
                                             * multiplicator)
