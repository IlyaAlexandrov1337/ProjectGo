from dlgo.agent.naive import RandomBot
from dlgo import goboard_normal as goboard
from dlgo import gotypes
from dlgo.utils import print_board, print_move, point_from_coords
from six.moves import input


def main():
    board_size = 19
    game = goboard.GameState.new_game(board_size)
    bot = RandomBot()

    while not game.is_over():
        print(chr(27) + "[2J")
        print_board(game.board)
        if game.next_player == gotypes.Player.black:
            human_move = input('Ваш ход: ').strip()
            if human_move == 'pass':
                move = goboard.Move.pass_turn()
            elif human_move == 'draw':
                move = goboard.Move.resign()
            else:
                point = point_from_coords(human_move)
                move = goboard.Move.play(point)
        else:
            move = bot.select_move(game)
        print_move(game.next_player, move)
        game = game.apply_move(move)


if __name__ == '__main__':
    main()
