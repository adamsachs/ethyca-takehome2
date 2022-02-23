from array import array
from enum import Enum
import datetime
from copy import deepcopy
from queue import Empty
from random import choice
import json
from typing import List
import numpy as np

# These are our "Values"
X = "X"
O = "O"
EMPTY = "."

class Result(Enum):
    """Enum class used to describe the state or result of a Game.
    """
    X_WINNER = "X is winner"
    O_WINNER = "O is winner"
    DRAW = "Game ended in a draw"
    ONGOING = "Game still ongoing"

class Board:
    """The Board class represents a tic-tac-toe board 
    and the operations that can be performed on it.

    A Board has a 2d numpy array that represents its state;
    the array is maintained internally this should not be accessed publicly.

    Boards can be made with variable sizes, but are always a square.
    """

    # board is a square, just need one "length" property
    _board_length: int

    # outer array is "y" axis (rows), inner arrays are "x" axis (columns)
    _state: np.array

    # availability keeps track of available spots as ints
    _available: set

    def __init__(self, cloned_board: 'Board' = None, board_length: int = 3) -> None:
        """Create a board.

        A board can be cloned off of an existing Board, if provided, or 
        it can be created from "scratch". If created from "scratch", the user can
        optionally provide a board "length."

        Args:
        cloned_board (optional, Board): the board to clone. Defaults to None.
        board_length (optional, int): the "length" (and "width") of the board to create.
            Defaults to 3.

        Raises:
            ValueError: If request board length property is below 0
                or is not a valid int
        """
        if cloned_board == None: # empty board
            # initialize "empty" board
            if board_length < 1:
                raise ValueError("Invalid board size provided")
            self._board_length = board_length
            self._state = np.full((board_length, board_length), EMPTY)

            # an optimization would be to initialize the availability
            # set in a random order here, so then we can just pop off later
            self._available = set()
            for i in range(board_length * board_length):
                self._available.add(i) 
        
        else: # cloned board
            self._board_length = cloned_board._board_length
            self._state = np.copy(cloned_board._state)
            self._available = cloned_board._available

    
    def update(self, x, y, value):
        """Update a board with a move

        Args:
        x (int): x coordinate of the move
        y (int): y coordinate of the move
        value (str): the value (player) of the move

        Raises:
            ValueError: If invalid coordinates are provided, or if
                the spot is already occupied, or if the value is invalid.
        """
        self.check_validity(x, y, value)
        self._state[y,x] = value
        self._available.remove(self._coord_to_number(x, y)) # remove from available numbers

    def _coord_to_number(self, x, y):
        """Translate a coordinate to its representative availability number

        Args:
        x (int): x coordinate
        y (int): y coordinate

        Returns:
            The representative availability number (int)
        """
        # y coordinate is row, x is column
        # y coordinate is multiplied, x is added
        return (self._board_length*y) + x

    def _number_to_coord(self, n):
        """Translate a availability number to its coordinates

        Args:
        n (int): availability number

        Returns:
            The x,y coordinates (tuple)
        """
        # x coordinate is added - so we mod it
        # y coordinate is multiplied - so we int divide it
        return n % self._board_length, n // self._board_length

    def check_validity(self, x, y, value):
        """Checks whether the provided move is valid on the current board

        Args:
            x (int): x coordinate
            y (int): y coordinate 
            value (int): value to put

        Raises:
            ValueError: if coordinates are invalid, if the coordinates are already occupied
                or if the value provided is not a valid value.
        """
        if x >= self._board_length or x < 0 or y >= self._board_length or y < 0:
            raise ValueError("Invalid coordinates provided")
        elif self._coord_to_number(x, y) not in self._available:
            raise ValueError("Provided coordinates already occupied")
        elif value not in [X, O]: # just to be safe garbage isn't passed
            raise ValueError("Invalid move provided")

    # checks for board winner
    def check_winner(self, x, y, value) -> bool:
        """Checks whether there is a winner on the board. 
        
        The coordinates and value of the most recent move
        are provided to allow for a quicker check.

        Args:
            x (int): x coordinate of most recent move
            y (int): y coordinate of most recent move
            value (str): value of the most recent move

        Returns:
            Whether or not there is a winner (bool)
        """
        diags = self._get_diagonals()
        return Board._check_array_winner(self._state[y], value) or Board._check_array_winner(self._get_column(x), value) or Board._check_array_winner(diags[0], value) or Board._check_array_winner(diags[1], value)
    
    @staticmethod
    def _check_array_winner(array_to_check: array, value: str) -> bool:
        """Utility method to check whether a given array is a winner,
         i.e. whether the array has only the specified value
        
        Args:
            array_to_check (array): the array to check
            value (str): value to check

        Returns:
            Whether or not the array is a winner,
            i.e. whether or not its elements are only the specified value
        """
        return np.all(array_to_check == value)

    def _get_column(self, x) -> array:
        return self._state[:,x]
        
    def _get_diagonals(self):
        """Gets the diagonals of the board as arrays
        
        Returns:
            A list of 2 arrays, each is a diagonal    
        """
        diags = list()
        diags.append(np.diag(self._state))
        diags.append(np.diag(np.fliplr(self._state)))
        return diags

    def check_draw(self) -> bool:
        # check whether available set is empty
        return self._available == set() 
    
    def get_available_coord(self) -> tuple:
        """Gets an available coordinate from the board.
        The coordinate is randomly chosen.
        
        Returns:
            A tuple representing the chosen x,y coordinates
        """
        
        # improve this, currently o(n) time complexity.
        # instead of randomly choosing from a list here
        # we could create the availability set in a random order
        # and simply pop off the first value here.
        return self._number_to_coord(choice(list(self._available)))

    def __str__(self) -> str:
        return ", ".join([str(r) for r in self._state])
    
    def __repr__(self) -> str:
        return ", ".join([str(r) for r in self._state])

    

class Move:
    """The Move class represents a move on a tic-tac-toe board.

    A Move can be thought of as the "state" of a tic-tac-toe game.
    A Move references a Board, and has some other attributes.

    A Move can be created from "scratch" (the first move of a game),
    or it can be created from a previous Move.
    
    Args:
        previous_move (Move): the previous Move that the newly created Move
            is following. Defaults to None (first move).
        x (int): The x coordinate of the Move. Defaults to None (first move).
        y (int): The y coordinate of the Move. Defaults to None (first move).
        value (str): The "value" ("player) of the Move. Defaults to None (first move).
        board_length (int): The size of the Board that should be created. Defaults to 3.
            This is only applicable if previous_move is not specified, i.e. on first move.

    Attributes:
        id (int): the move ID
        timestamp (datetime.datetime): the time the move was made
        board (Board): the Board after the move
        result (Result): the Result (of the game) after the move
        last_moved (str): the "player" or "value" that last moved
    
    """

    id: int = None
    timestamp: datetime.datetime = None
    board: Board = None
    result: Result = None
    last_moved: str = None    

    def __init__(self, previous_move: 'Move' = None, x: int = None, y: int = None, value: str = None, board_length: int = 3) -> None:
        self.timestamp = datetime.datetime.now()

        if previous_move is None: # first move
            self.id = 0
            self.board = Board(board_length=board_length) # empty board to start
            self.result = Result.ONGOING
        else: # a following move
            if previous_move.result != Result.ONGOING:
                raise ("Cannot make a new move on a finished game!")

            self.id = previous_move.id + 1 # increment move ID
            self.board = Board(cloned_board=previous_move.board) # board is based on previous move's board
            self.board.update(x, y, value) # update the board with the move
            if self.board.check_winner(x, y, value): # check for winners
                if value is X:
                    self.result = Result.X_WINNER
                elif value is O:
                    self.result = Result.O_WINNER
            elif self.board.check_draw(): # check for draw
                self.result = Result.DRAW
            else:
                self.result = Result.ONGOING
            self.last_moved = value # update last_moved pointer

    def __str__(self) -> str:
        strobj = {
            "move_id": self.id ,
            "timestamp": str(self.timestamp),
            "last_moved": self.last_moved,
            "board_state": str(self.board),
            "game_state": self.result.value
        }
        return json.dumps(strobj, sort_keys=True, indent=4)
    
    def __repr__(self) -> str:
        strobj = {
            "move_id": self.id ,
            "timestamp": str(self.timestamp),
            "last_moved": self.last_moved,
            "board_state": str(self.board),
            "game_state": self.result.value
        }
        return json.dumps(strobj, sort_keys=True, indent=4)

class Game:
    """The Game class represents a move on a tic-tac-toe game.

    A Game can be thought of as the record for a game.
    A Game contains basic attributes about the game.
    It also maintains an array of Moves that have been made in the game.

    Args:
        game_id (int): the ID to use for the game
        board_length (int): the "length" (and width) of the Board to use for the game.
            Default is 3. 
    
    Attributes:
        id (int): the game ID
        started (datetime.datetime): the time the game was stated
        moves (numpy.Array): the array of Moves that have been made in the game,
            chronologically ordered (most recent is last)
        last_move (Move): a pointer to the most recent move of the game.
            This can be used to conveniently get the current "state" of the game.
    
    """

    id: int
    started: datetime.datetime
    moves: np.array
    last_move: Move

    def __init__(self, game_id, board_length:int = 3) -> None:
        self.id = game_id
        self.started = datetime.datetime.now()
        self.last_move = Move(board_length=board_length)
        self.moves = [self.last_move]
    
    def make_move(self, x, y, value) -> Result:
        """Make a move in the game

        Args:
        x (int): x coordinate of the move
        y (int): y coordinate of the move
        value (str): the value (player) of the move

        Returns:
            The Result of the move, i.e. the state of the game after the move.

        Raises:
            ValueError: If the game is not active/ongoing,
                if invalid coordinates are provided, if the spot is already occupied,
                or if the value is invalid.
        """
        if self.last_move.result != Result.ONGOING:
            raise ValueError("Cannot make a new move on a finished game!")
        else:
            self.last_move = Move(self.last_move, x, y, value)
            self.moves.append(self.last_move)
            # check for winner and return something
            return self.last_move.result
    
    def make_computer_move(self, value: str=O) -> Result:
        """Make a computer move in the game.

        Currently this just chooses a random available spot on the board.
        The functionality could be improved to make a "smarter" choice.

        Args:
        value (str): the value (player) of the move. Default is O.

        Returns:
            The Result of the move, i.e. the state of the game after the move.
        """
        
        # get random available coordinate for next move
        # here's where we could plug in some smarts if we wanted
        x, y = self.last_move.board.get_available_coord()
        # make move to that coordiante
        return self.make_move(x, y, value)
    
    def get_moves(self, i: int = None) -> List[Move]:
        """Convenience method to get one or more of the games move, by index.
        If no index is provided, then all games will be returned as an array.

        Args:
            i (int): index of the move to get. Default is None (all moves).

        Returns:
            The Move (or array of Moves) requested
        """
        if i is not None:
            if i > len(self.moves) -1 or i < 0:
                raise ValueError("Invalid move index provided")
            else:
                return [self.moves[i]]
        else:
            return self.moves
    
    
    def __str__(self) -> str:
        strobj = {
            "game_id": self.id ,
            "started_time": str(self.started),
            "board_state": str(self.last_move.board),
            "last_played": self.last_move.last_moved,
            "game_state": self.last_move.result.value
        }
        return json.dumps(strobj, sort_keys=True, indent=4)
    
    def __repr__(self) -> str:
        strobj = {
            "game_id": self.id ,
            "started_time": str(self.started),
            "board_state": str(self.last_move.board),
            "last_played": self.last_move.last_moved,
            "game_state": self.last_move.result.value 
        }
        return json.dumps(strobj, sort_keys=True, indent=4)
