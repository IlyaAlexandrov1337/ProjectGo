from dlgo.gotypes import Player, Point


def capture_diff(game_state):
    black_stones = 0
    white_stones = 0
    for r in range(1, game_state.board.num_rows + 1):
        for c in range(1, game_state.board.num_cols + 1):
            p = Point(r, c)
            color = game_state.board.get(p)
            if color == Player.black:
                black_stones += 1
            elif color == Player.white:
                white_stones += 1
    # Расчет разницы между количеством черных и белых камней на доске. Результат будет совпадать
    # с разницей в количестве захваченных камней, если ни один из игроков не пасовал на более ранних этапах игры
    diff = black_stones - white_stones
    # Если очередь хода за черными, возвращается результат вычитания: (черные камни) – (белые камни)
    if game_state.next_player == Player.black:
        return diff
    # Если очередь хода за белыми, возвращается результат вычитания: (белые камни) – (черные камни)
    return -1 * diff