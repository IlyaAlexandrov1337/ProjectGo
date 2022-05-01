import enum
import random

from dlgo.agent import Agent

__all__ = [
    'MinimaxAgent',
]


class GameResult(enum.Enum):
    loss = 1
    draw = 2
    win = 3


def reverse_game_result(game_result):
    if game_result == GameResult.loss:
        return game_result.win
    if game_result == GameResult.win:
        return game_result.loss
    return GameResult.draw


def best_result(game_state):
    if game_state.is_over():
        # Игра уже закончена
        if game_state.winner() == game_state.next_player:
            # Победа игрока
            return GameResult.win
        elif game_state.winner() is None:
            # Ничья
            return GameResult.draw
        else:
            # Победа противника
            return GameResult.loss
    best_result_so_far = GameResult.loss
    for candidate_move in game_state.legal_moves():
        # Вычислить, как будет выглядеть доска в случае выбора данного хода
        next_state = game_state.apply_move(candidate_move)
        # Определение лучшего хода противника
        opponent_best_result = best_result(next_state)
        # Что бы ни было нужно противнику, игроку-агенту нужно противоположное.
        our_result = reverse_game_result(opponent_best_result)
        # Узнать, превосходит ли этот результат все рассмотренные до этого варианты
        if our_result.value > best_result_so_far.value:
            best_result_so_far = our_result
    return best_result_so_far


class MinimaxAgent(Agent):
    def select_move(self, game_state):
        winning_moves = []
        draw_moves = []
        losing_moves = []
        # Циклическая обработка всех допустимых ходов
        for possible_move in game_state.legal_moves():
            # Определение состояния доски при выборе конкретного хода
            next_state = game_state.apply_move(possible_move)
            # Поскольку следующий ход делает противник игрока-агента, вычислить его наилучший возможный результат
            opponent_best_outcome = best_result(next_state)
            # Результат игрока-агента будет противоположным.
            our_best_outcome = reverse_game_result(opponent_best_outcome)
            # Классификация хода в зависимости от его результата
            if our_best_outcome == GameResult.win:
                winning_moves.append(possible_move)
            elif our_best_outcome == GameResult.draw:
                draw_moves.append(possible_move)
            else:
                losing_moves.append(possible_move)
        # Выбор хода, обеспечивающего наилучший для игрока-агента результат.
        if winning_moves:
            return random.choice(winning_moves)
        if draw_moves:
            return random.choice(draw_moves)
        return random.choice(losing_moves)
