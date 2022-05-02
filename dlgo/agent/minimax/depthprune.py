import random

from dlgo.agent import Agent
from dlgo.agent.minimax.helpers import capture_diff
from dlgo.scoring import GameResult

__all__ = [
    'DepthPrunedAgent',
]

MAX_SCORE = 999999
MIN_SCORE = -999999


def reverse_game_result(game_result):
    if game_result == GameResult.loss:
        return game_result.win
    if game_result == GameResult.win:
        return game_result.loss
    return GameResult.draw


def best_result(game_state, max_depth, eval_fn):
    # Если игра окончена, уже известен победитель
    if game_state.is_over():
        if game_state.winner() == game_state.next_player:
            return MAX_SCORE
        else:
            return MIN_SCORE

    if max_depth == 0:
        return eval_fn(game_state)

    best_so_far = MIN_SCORE
    # Циклическая обработка всех допустимых ходов
    for candidate_move in game_state.legal_moves():
        # Вычислить, как будет выглядеть доска в случае выбора этого хода
        next_state = game_state.apply_move(candidate_move)
        # Вычислить лучший результат противника, исходя из этой позиции
        opponent_best_result = best_result(
            next_state, max_depth - 1, eval_fn)
        # Что бы ни было нужно противнику, игроку-агенту нужно противоположное
        our_result = -1 * opponent_best_result
        # Узнать, превосходит ли этот результат все рассмотренные до этого варианты
        if our_result > best_so_far:
            best_so_far = our_result

    return best_so_far


class DepthPrunedAgent(Agent):
    def __init__(self, max_depth, eval_fn=capture_diff):
        Agent.__init__(self)
        self.max_depth = max_depth
        self.eval_fn = eval_fn

    def select_move(self, game_state):
        best_moves = []
        best_score = None
        # Циклическая обработка всех допустимых ходов
        for possible_move in game_state.legal_moves():
            # Вычислить игровое состояние при выборе этого хода
            next_state = game_state.apply_move(possible_move)
            # Определение лучшего результата противника, исходя из этой позиции
            opponent_best_outcome = best_result(next_state, self.max_depth, self.eval_fn)
            # Что бы ни было нужно противнику, игроку-агенту нужно противоположное
            our_best_outcome = -1 * opponent_best_outcome
            if (not best_moves) or our_best_outcome > best_score:
                # Пока это лучший ход
                best_moves = [possible_move]
                best_score = our_best_outcome
            elif our_best_outcome == best_score:
                # Этот ход так же хорош, как и предыдущий лучший ход.
                best_moves.append(possible_move)
        # Выбрать ход случайным образом среди всех одинаково хороших ходов
        return random.choice(best_moves)
