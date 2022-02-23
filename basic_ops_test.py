import unittest
import numpy as np
from tic_tac_toe import Game, Result, EMPTY, X, O

class TestTicTacToeMethods(unittest.TestCase):

    EMPTY_BOARD = np.full((3, 3), EMPTY)
    EMPTY_BOARD_5 = np.full((5, 5), EMPTY)

    def test_create_game(self):
        g = Game(0)
        self.assertEqual(g.id, 0)
        moves = g.get_moves()
        self.assertEqual(len(moves), 1)
        m = moves[0]
        self.assertEqual(m.result, Result.ONGOING)
        np.testing.assert_equal(m.board._state, TestTicTacToeMethods.EMPTY_BOARD)

    def test_create_game_different_length(self):
        g = Game(0, board_length=5)
        self.assertEqual(g.id, 0)
        moves = g.get_moves()
        self.assertEqual(len(moves), 1)
        m = moves[0]
        self.assertEqual(m.result, Result.ONGOING)
        np.testing.assert_equal(m.board._state, TestTicTacToeMethods.EMPTY_BOARD_5)

    def test_make_moves(self):
        g = Game(0)
        r = g.make_move(0, 2, X)
        self.assertEqual(r, Result.ONGOING)
        moves = g.get_moves()
        self.assertEqual(len(moves), 2)
        # first move is still empty board
        m = moves[0]
        self.assertEqual(m.result, Result.ONGOING) 
        np.testing.assert_equal(m.board._state, TestTicTacToeMethods.EMPTY_BOARD)
        # second move is still ongoing, but with one value
        m = moves[1]
        self.assertEqual(m.result, Result.ONGOING) 
        self.assertEqual(m.board._state[2,0], X)
        
        # 3rd move: O goes in (1,2)
        r = g.make_move(1, 2, O)
        self.assertEqual(r, Result.ONGOING)
        moves = g.get_moves()
        m = moves[2]
        self.assertEqual(len(moves), 3)
        self.assertEqual(m.result, Result.ONGOING) 
        self.assertEqual(m.board._state[2,1], O)

    def test_move_same_spot(self):
        g = Game(0)
        g.make_move(0, 2, X)
        self.assertRaises(ValueError, g.make_move, 0, 2, O)

        g.make_move(1, 2, O)
        self.assertRaises(ValueError, g.make_move, 1, 2, O)

        g.make_move(2, 1, X)
        self.assertRaises(ValueError, g.make_move, 2, 1, O)

    def test_move_larger_board(self):
        g = Game(0, board_length=5)
        self.assertRaises(ValueError, g.make_move, 5, 5, X)
        g.make_move(4, 4, X)
        m = g.get_moves()[1]
        self.assertEqual(m.board._state[4,4], X)

        g.make_move(1, 2, O)
        m = g.get_moves()[2]
        self.assertEqual(m.board._state[2,1], O)

        

    def test_win(self):
        g = Game(0)
        g.make_move(0, 2, X)
        g.make_move(0, 1, O)
        g.make_move(1, 2, X)
        g.make_move(0, 0, O)
        r = g.make_move(2, 2, X)
        self.assertEqual(r, Result.X_WINNER)
        self.assertRaises(ValueError, g.make_move, 1, 1, O)
    
    def test_draw(self):
        g = Game(0)
        g.make_move(0, 0, X)
        g.make_move(0, 1, O)
        g.make_move(0, 2, X)
        g.make_move(1, 1, O)
        g.make_move(1, 0, X)
        g.make_move(1, 2, O)
        g.make_move(2, 1, X)
        g.make_move(2, 0, O)
        r = g.make_move(2, 2, X)
        self.assertEqual(r, Result.DRAW)
        self.assertRaises(ValueError, g.make_move, 1, 1, O)


if __name__ == '__main__':
    unittest.main()