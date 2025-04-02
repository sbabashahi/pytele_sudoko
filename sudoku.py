from dataclasses import dataclass


class SudokuException(Exception):
    pass


@dataclass
class Sudoku:
    matrix: list[list[int]]

    @staticmethod
    def list_to_matrix(raw_sudoku: list[int]) -> list[list[int]]:
        if len(raw_sudoku) != 81:
            raise SudokuException('Sudoku list must have 81 elements')
        return [raw_sudoku[i:i+9] for i in range(0, 81, 9)]

    def solve(self) -> list[list[int]]:
        self._check_matrix_is_valid()
        if self._solve_sudoku():
            return self.matrix
        raise SudokuException('Sudoku cannot be solved :sad_slava:')

    def _solve_sudoku(self) -> bool:
        empty_pos = self._next_empty_pos()
        if empty_pos is None:
            return True  # Solution found!

        row, col = empty_pos

        for num in range(1, 10):
            if self.is_valid(num, row, col):
                self.matrix[row][col] = num  # Try this number

                if self._solve_sudoku():
                    return True

                self.matrix[row][col] = 0  # Backtrack

        return False

    @staticmethod
    def humanized_board(board: list[list[int]] | list[int]) -> str:
        temp = ''
        if isinstance(board[0], int):  # 1 col or 1 row, could be improved later
            return ' '.join(map(str, board))

        for row in range(len(board)):
            if row % 3 == 0 and row != 0:
                temp += ('-' * 39) + '\n'
            for col in range(len(board[row])):
                if col % 3 == 0 and col != 0:
                    temp += ' | '
                temp += f' {(board[row][col])} '
            temp += '\n'
        return temp

    def _next_empty_pos(self) -> tuple[int, int] | None:
        """
        Find next empty position in the sudoku which mean there is 0 in that cell
        :return:
        """
        for row in range(len(self.matrix)):
            for col in range(len(self.matrix[row])):
                if self.matrix[row][col] == 0:  # Empty cells are represented by 0
                    return row, col
        return None

    def get_section(self, section: str, number: int) -> list[list[int]] | list[int]:
        if section == 'f':
            return self.matrix

        if len(section) != 1 or section.lower() not in {'s', 'r', 'c'} or number not in range(1, 10):
            raise SudokuException(
                f'Section {section} or number {number} is not valid'
                'section options are: `s`, `r`, `c`'
                'number options are: `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`'
            )
        match section:
            case 's':
                sections = [
                    (0, 0),
                    (0, 3),
                    (0, 6),
                    (3, 0),
                    (3, 3),
                    (3, 6),
                    (6, 0),
                    (6, 3),
                    (6, 6),
                ]
                i, j = sections[number - 1]
                return [self.matrix[i][j:j+3] for i in range(i, i+3)]
            case 'r':
                return self.matrix[number-1]
            case 'c':
                return [self.matrix[i][number-1] for i in range(0, 9)]

    def is_valid(self, num: int, row: int, col: int):
        """Checks if a number can be placed at the given position."""
        # Check the row
        if num in self.get_section('r', row + 1):
            return False

        if num in self.get_section('c', col + 1):
            return False

        # Check the 3x3 sub-grid
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.matrix[i][j] == num:
                    return False

        return True

    def _check_matrix_is_valid(self) -> None:
        if len(self.matrix) != 9:
            raise SudokuException(f'The number of rows is {len(self.matrix)} and is not correct.')
        for r_ind, row in enumerate(self.matrix):
            if len(row) != 9:
                raise SudokuException(f'The number of columns in row {r_ind} is {len(row)} and is not correct.')
            for c_ind, item in enumerate(row):
                if not isinstance(item, int) or item < 0 or item > 9:
                    raise SudokuException(f'The value {item}, index {r_ind}, {c_ind} is out of range.')


