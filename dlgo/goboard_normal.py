from copy import deepcopy
from dlgo import zobrist
from dlgo.gotypes import Player, Point
from dlgo.scoring import compute_game_result


# Задаются возможные действия игрока –is_play, is_pass или is_resign.
class Move:
    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    # Этот ход предполагает размещение камня на доске.
    @classmethod
    def play(cls, point):
        return Move(point=point)

    # Этот ход предполагает пропуск хода.
    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)

    # Этот ход предполагает выход из игры.
    @classmethod
    def resign(cls):
        return Move(is_resign=True)


# GoString – цепочка связанных камней одного цвета.
class GoString:
    def __init__(self, color, stones, liberties):
        self.color = color
        # Множества камней и степеней свободы теперь являются неизменяемыми.
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)

    # Метод without_liberty заменил предыдущий метод remove_liberty
    def without_liberty(self, point):
        new_liberties = self.liberties - {point}
        return GoString(self.color, self.stones, new_liberties)

    # метод with_liberty заменил предыдущий метод add_liberty.
    def with_liberty(self, point):
        new_liberties = self.liberties | {point}
        return GoString(self.color, self.stones, new_liberties)

    # Возвращает новую цепочку, содержащую все камни обеих цепочек
    def merged_with(self, go_string):
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | go_string.liberties) - combined_stones)

    @property
    def num_liberties(self):
        return len(self.liberties)

    def __eq__(self, other):
        return isinstance(other, GoString) and \
               self.color == other.color and \
               self.stones == other.stones and \
               self.liberties == other.liberties


# Доска инициализируется в виде пустой сетки, состоящей из заданного количества строк и столбцов.
class Board:
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}
        self._hash = zobrist.EMPTY_BOARD

    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and 1 <= point.col <= self.num_cols

    # Возвращает содержимое точки на доске: сведения об игроке,
    # если в этой точке находится камень, в противном случае – None.
    def get(self, point):
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color

    # Возвращает всю цепочку камней, если в этой точке находится камень, в противном случае – None.
    def get_go_string(self, point):
        string = self._grid.get(point)
        if string is None:
            return None
        return string

    def _remove_string(self, string):
        for point in string.stones:
            # Удаление цепочки камней может увеличить степени свободы других цепочек.
            for neighbor in point.neighbors():
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:
                    self._replace_string(neighbor_string.with_liberty(point))
            self._grid[point] = None
            # При использовании Zobrist-хеширования необходимо отменить применение хеш-значения для этого хода.
            self._hash ^= zobrist.HASH_CODE[point, string.color]

    # Этот новый вспомогательный метод обновляет сетку доски.
    def _replace_string(self, new_string):
        for point in new_string.stones:
            self._grid[point] = new_string

    # Сначала исследуются непосредственные соседи конкретной точки.
    def place_stone(self, player, point):
        assert self.is_on_grid(point)
        assert self._grid.get(point) is None
        adjacent_same_color = []
        adjacent_opposite_color = []
        liberties = []
        for neighbor in point.neighbors():
            if not self.is_on_grid(neighbor):
                continue
            neighbor_string = self._grid.get(neighbor)
            if neighbor_string is None:
                liberties.append(neighbor)
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_string)
            else:
                if neighbor_string not in adjacent_opposite_color:
                    adjacent_opposite_color.append(neighbor_string)
        # До этой строки метод place_stone остается прежним.
        new_string = GoString(player, [point], liberties)
        # Объединение всех смежных цепочек камней одного цвета.
        for same_color_string in adjacent_same_color:
            new_string = new_string.merged_with(same_color_string)
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string

        # Применение хеш-кода для данной точки и игрока.
        self._hash ^= zobrist.HASH_CODE[point, player]
        # Уменьшение количества степеней свободы соседних цепочек камней противоположного цвета.
        for other_color_string in adjacent_opposite_color:
            # Уменьшение количества степеней свободы любых смежных цепочек камней другого цвета.
            replacement = other_color_string.without_liberty(point)
            if replacement.num_liberties:
                self._replace_string(other_color_string.without_liberty(point))
            else:
                # Удаление цепочек камней другого цвета с нулевой степенью свободы.
                self._remove_string(other_color_string)
        # Удаление с доски цепочек камней противоположного цвета с нулевой степенью свободы.
        for other_color_string in adjacent_opposite_color:
            if other_color_string.num_liberties == 0:
                self._remove_string(other_color_string)

    def __eq__(self, other):
        return isinstance(other, Board) and \
               self.num_rows == other.num_rows and \
               self.num_cols == other.num_cols and self._grid == other._grid

    # Возврат текущего Zobrist-хеша доски
    def zobrist_hash(self):
        return self._hash


class GameState:
    def __init__(self, board, next_player, previous, move):
        self.board = board
        self.next_player = next_player
        self.previous_state = previous
        if self.previous_state is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(
                previous.previous_states |
                {(previous.next_player, previous.board.zobrist_hash())})
        self.last_move = move

    # Возвращает новое игровое состояние после совершения хода.
    def apply_move(self, move):
        if move.is_play:
            next_board = deepcopy(self.board)
            next_board.place_stone(self.next_player, move.point)
        else:
            next_board = self.board
        return GameState(next_board, self.next_player.other, self, move)

    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    def is_over(self):
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True
        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False
        return self.last_move.is_pass and second_last_move.is_pass

    def is_move_self_capture(self, player, move):
        if not move.is_play:
            return False
        next_board = deepcopy(self.board)
        next_board.place_stone(player, move.point)
        new_string = next_board.get_go_string(move.point)
        return new_string.num_liberties == 0

    @property
    def situation(self):
        return self.next_player, self.board

    # Быстрая проверка игровых состояний на применимость правила ко с помощью Zobrist-хешей
    def does_move_violate_ko(self, player, move):
        if not move.is_play:
            return False
        next_board = deepcopy(self.board)
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board.zobrist_hash())
        return next_situation in self.previous_states

    def is_valid_move(self, move):
        if self.is_over():
            return False
        if move.is_pass or move.is_resign:
            return True
        return (
                self.board.get(move.point) is None and
                not self.is_move_self_capture(self.next_player, move) and
                not self.does_move_violate_ko(self.next_player, move))

    def legal_moves(self):
        moves = []
        for row in range(1, self.board.num_rows + 1):
            for col in range(1, self.board.num_cols + 1):
                move = Move.play(Point(row, col))
                if self.is_valid_move(move):
                    moves.append(move)
        # Эти два хода всегда возможны.
        moves.append(Move.pass_turn())
        moves.append(Move.resign())

        return moves

    def winner(self):
        if not self.is_over():
            return None
        if self.last_move.is_resign:
            return self.next_player
        game_result = compute_game_result(self)
        return game_result.winner
