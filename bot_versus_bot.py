from dlgo.agent.naive import RandomBot
from dlgo import agent
from dlgo import goboard_normal as goboard
from dlgo import gotypes
from dlgo.utils import print_board, print_move
import time


def main():
    dct = {}
    board_size = 19
    game = goboard.GameState.new_game(board_size)
    bots = {
        gotypes.Player.black: agent.naive.RandomBot(),
        gotypes.Player.white: agent.naive.RandomBot(),
    }
    for i in range(50):
        game = goboard.GameState.new_game(board_size)
        while not game.is_over():
            # Установка таймера на 0,3 секунды обеспечивает задержку между отображением ходов ботов.
            # time.sleep(0.3)

            # Перед выполнением каждого хода экран очищается, благодаря чему
            # доска всегда отображается в одном и том же месте командной строки.
            #print(chr(27) + "[2J")
            #print_board(game.board)
            bot_move = bots[game.next_player].select_move(game)
            #print_move(game.next_player, bot_move)
            game = game.apply_move(bot_move)
        print(f"Winner: {game.winner()}")
        if dct.get(game.winner()):
            dct[game.winner()] += 1
        else:
            dct[game.winner()] = 1
    print(dct)


if __name__ == '__main__':
    main()
