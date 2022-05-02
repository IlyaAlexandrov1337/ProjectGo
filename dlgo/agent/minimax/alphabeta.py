import random

from dlgo.agent import Agent
from dlgo.gotypes import Player
from dlgo.agent.minimax.helpers import capture_diff

__all__ = [
    'AlphaBetaAgent',
]

MAX_SCORE = 999999
MIN_SCORE = -999999


def alpha_beta_result(game_state, max_depth, best_black, best_white, eval_fn):
    # проверка на предмет окончания игры
    if game_state.is_over():
        if game_state.winner() == game_state.next_player:
            return MAX_SCORE
        else:
            return MIN_SCORE
    # Достижение максимальной глубины поиска. Используйте свой эвристический метод для оценки последовательности ходов.
    if max_depth == 0:
        return eval_fn(game_state)

    best_so_far = MIN_SCORE
    # Циклическая обработка всех допустимых ходов
    for candidate_move in game_state.legal_moves():
        # Вычислить, как будет выглядеть доска в случае выбора этого хода
        next_state = game_state.apply_move(candidate_move)
        # Определение лучшего результата противника, исходя из этой позиции
        opponent_best_result = alpha_beta_result(
            next_state, max_depth - 1,
            best_black, best_white,
            eval_fn)
        # Что бы ни было нужно противнику, игроку-агенту нужно противоположное
        our_result = -1 * opponent_best_result

        if our_result > best_so_far:
            best_so_far = our_result
        # Узнать, превосходит ли этот результат все рассмотренные до этого варианты.
        if game_state.next_player == Player.white:
            # Обновление лучшего результата для игрока белыми.
            if best_so_far > best_white:
                best_white = best_so_far
            # Выбор хода для белых, который должен быть достаточно сильным, чтобы перебить предыдущий ход черных
            outcome_for_black = -1 * best_so_far
            # После нахождения варианта, превосходящего лучший ход черных, поиск можно прекратить
            if outcome_for_black < best_black:
                return best_so_far
        elif game_state.next_player == Player.black:
            # Обновление лучшего результата для игрока черными.
            if best_so_far > best_black:
                best_black = best_so_far
            # Выбор хода для черных, который должен быть достаточно сильным, чтобы перебить предыдущий ход белых.
            outcome_for_white = -1 * best_so_far
            if outcome_for_white < best_white:
                return best_so_far

    return best_so_far


class AlphaBetaAgent(Agent):
    def __init__(self, max_depth, eval_fn=capture_diff):
        Agent.__init__(self)
        self.max_depth = max_depth
        self.eval_fn = eval_fn

    def select_move(self, game_state):
        best_moves = []
        best_score = None
        best_black = MIN_SCORE
        best_white = MIN_SCORE
        # Циклическая обработка всех допустимых ходов
        for possible_move in game_state.legal_moves():
            # Вычислить игровое состояние при выборе этого хода
            next_state = game_state.apply_move(possible_move)
            # Определение лучшего результата противника, исходя из этой позиции
            opponent_best_outcome = alpha_beta_result(
                next_state, self.max_depth,
                best_black, best_white,
                self.eval_fn)
            # Что бы ни было нужно противнику, игроку-агенту нужно противоположное
            our_best_outcome = -1 * opponent_best_outcome
            if (not best_moves) or our_best_outcome > best_score:
                # This is the best move so far.
                best_moves = [possible_move]
                best_score = our_best_outcome
                if game_state.next_player == Player.black:
                    best_black = best_score
                elif game_state.next_player == Player.white:
                    best_white = best_score
            elif our_best_outcome == best_score:
                # Этот ход так же хорош, как и предыдущий лучший ход.
                best_moves.append(possible_move)
        # Выбрать ход случайным образом среди всех одинаково хороших ходов
        return random.choice(best_moves)
