

from typing import Self
from collections.abc import Iterable

class Matrix:
    __slots__ = ["data", "dimension"]
    type Number = float|int
    def __init__(self, dimesion:int, data:list[Number] = None):
        self.data = data or [[0] * dimesion for _ in range(dimesion)]
        self.dimension = dimesion
    
    def __str__(self) -> str:
        PRECISION = 3
        out = ""
        data = tuple(map(lambda f:f"{f:.{PRECISION}f}", self.data))
        dim = self.dimension
        max_digit = max(map(len, data))
        for y in range(self.dimension):
            for x in range(self.dimension):
                out += f"{data[y * dim + x]:<{max_digit + 3}}"
            out += "\n"
        return out.replace(f"-{0:.{PRECISION}f}", f"{0:.{PRECISION}f} ")

    def print(self, positions:Iterable[tuple[int, int]]=[]) -> None:
        PRECISION = 3
        out = ""
        data = tuple(map(lambda f:f"{f:.{PRECISION}f}", self.data))
        dim = self.dimension
        max_digit = max(map(len, data))
        for y in range(self.dimension):
            for x in range(self.dimension):
                if (y, x) in positions:
                    out += f">{data[y * dim + x]:<{max_digit + 1}}<"
                else:
                    out += f"{data[y * dim + x]:<{max_digit + 3}}"
            out += "\n"
        print(out.replace(f"{0:.{PRECISION}f}", f"-{0:.{PRECISION}f}"))

    @staticmethod
    def get_identity_matrix(dimesion:int) -> Self:
        data = ([1.0] + [0.0] * dimesion) * (dimesion - 1) + [1.0]
        return Matrix(dimesion, data)
    
    def __eq__(self, mat:Self) -> bool:
        return self.dimension == mat.dimension and self.data == mat.data
    
    def __getitem__(self, position:tuple[int, int]) -> Number:
        return self.data[position[0] * self.dimension + position[1]]
    
    def __setitem__(self, position:tuple[int, int], value:Number) -> Number:
        self.data[position[0] * self.dimension + position[1]] = value
    
    def _swap_row(self, row1_no:int, row2_no:int) -> None:
        dim = self.dimension
        row1_starting = row1_no * dim
        row2_starting = row2_no * dim
        for col_no in range(dim):
            self.data[row1_starting + col_no], self.data[row2_starting + col_no] = self.data[row2_starting + col_no], self.data[row1_starting + col_no]
    
    def _mul_row(self, row_no:int, multiplicator:Number) -> None:
        dim = self.dimension
        row_starting = row_no * dim
        for col_no in range(dim):
            self.data[row_starting + col_no] *= multiplicator
    
    def _sub_multiples_of_row(
        self, 
        minuend_row_no:int, 
        substrachend_row_no:int, 
        multiplicator:Number
    ) -> None:
        dim = self.dimension
        minuend_starting = minuend_row_no * dim
        substrachend_starting = substrachend_row_no * dim
        for col_no in range(dim):
            self.data[minuend_starting + col_no] -= self.data[substrachend_starting + col_no] * multiplicator

    def get_inverse(self) -> Self|None:
        """
        Gaussian Elimination

        Return `None` if the inverse does not exist
        """
        dim = self.dimension
        mat = Matrix(dim, self.data[:])
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
            # print(f"{pivot_no=}")
            # mat.print([(pivot_no, pivot_no)])
            # inverse.print()
            # print()
            multiplicator = 1 / mat[pivot_no, pivot_no]
            inverse._mul_row(pivot_no, multiplicator)
            mat._mul_row(pivot_no, multiplicator)
            for row_no in range(pivot_no + 1, dim):
                # print(f"{row_no=}")
                # mat.print([(row_no, pivot_no)])
                # inverse.print()
                # print()
                multiplicator = mat[row_no, pivot_no]
                mat._sub_multiples_of_row(row_no, pivot_no, multiplicator)
                inverse._sub_multiples_of_row(row_no, pivot_no, multiplicator)
        # Make non pivots 0
        # `dim - 1` iterations excluding last row
        for pivot_no in range(dim - 2, -1, -1):
            for col_no in range(pivot_no + 1, dim):
                # print()
                # mat.print([(pivot_no, col_no)])
                # inverse.print([(pivot_no, col_no)])
                inverse._sub_multiples_of_row(pivot_no, col_no, mat[pivot_no, col_no])
        # inverse.print()
        return inverse

    def mul_vector(self, vector:Iterable) -> tuple:
        dim = self.dimension
        if len(vector) != dim:
            raise ValueError("Invalid dimension")
        return tuple(sum(v * u for v, u in zip(vector, self.data[row_starting:row_starting + dim])) for row_starting in range(0, len(self.data), dim))

    def __mul__(self, matrix:Self) -> Self:
        dim = self.dimension
        dim_squared = len(self.data)
        if matrix.dimension != dim:
            raise ValueError("Invalid dimension")
        matrix_T = matrix.get_transposed()
        return Matrix(
            dim,
            [
                sum(
                    v * u
                    for v, u in zip(
                        self.data[row1_starting:row1_starting + dim],
                        matrix_T.data[row2_starting:row2_starting + dim], 
                    )
                )
                for row1_starting in range(0, dim_squared, dim)
                for row2_starting in range(0, dim_squared, dim)
            ]
        )


    def get_transposed(self) -> Self:
        dim = self.dimension
        return Matrix(
            dim, 
            [
                self.data[j * dim + i] 
                    for i in range(dim)
                        for j in range(dim)
            ]    
        )

