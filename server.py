from flask import Flask, Request, jsonify, request
from tic_tac_toe import Game, Result
import logging

app = Flask(__name__)

# HTTP Method constants. Only GET and POST supported for now.
GET = 'GET'
POST = 'POST'

# this is our "database". it's going to be a list(Game).
# it's a hack - data should not be stored across sessions/requests like this.
# but it seems to work for basic, non-concurent client usage.
# really we should store the game objects in a db,
# whose state persists, is decoupled from the web app, and safely supports
# concurrent reads and writes.
stored_games = list()

# /games endpoint to create and get Games
@app.route("/games", methods= {GET, POST})
def games():
    if request.method == POST: # create game
        try:
            board_length = get_board_length(request=request)
        except:
            return "Invalid board length specified", 400
        
        if (board_length == None): # no board_length specified, use default
            # the new game's ID is simply the index of game list
            game = Game(len(stored_games))
        else: # board length specified
            board_length = int(board_length)
            game = Game(len(stored_games), int(board_length))
                
        stored_games.append(game)
        return str(game)
    
    elif request.method == GET: # get game(s)
        game_id = request.args.get("game_id", '')
        if (game_id == ''): # no ID provided, return all games
            return str(stored_games)
        else:
            try:
                game = get_game(game_id)
                return str([game])
            except:
                return "Requested game not found", 404

# /moves endpoint to make and get moves
@app.route("/moves", methods= {GET, POST})
def moves():
    if request.method == POST: # make a move
        game_id = request.args.get("game_id", '')
        if (game_id == ''): # no ID provided, return all games
            return "Please provide a game ID for your move", 400
        try:
            game = get_game(game_id) # retrieve the game
            x, y = parse_move_request(request=request) # parse coordinates from req
            result = game.make_move(x, y, "X") # actually make the specified move on the game
            if result == Result.ONGOING: # if game hasn't ended, make a move for computer
                result = game.make_computer_move("O")
            return str(game) # return current game state
        except:
            logging.exception("Invalid move specified")
            return "Invalid move specified", 400

    elif request.method == GET: # get move(s)
        game_id = request.args.get("game_id", '')
        if (game_id == ''): # must provide a game ID
            return "Please provide a game ID for your move", 400
        
        game = get_game(game_id) # retrieve game
        move_id = request.args.get("move_id", '')
        if (move_id == ''): # no ID provided, return all moves
            moves = game.get_moves()
        else:
            moves = game.get_moves(int(move_id))
        return str(moves)



def get_game(id) -> Game:
    """ Gets a game by ID
    
    Args:
        id: id of the game, an int
    
    Returns:
        The retrieved Game
    """
    try:
        id = int(id) # catch invalid ID
    except:
        raise ValueError("Invalid game ID provided")
    if (id < 0 or id >= len(stored_games)):
        raise ValueError("Invalid game ID provided")
    else:
        return stored_games[id]

def get_board_length(request: Request):
    """ Gets the board length parameter

    Args:
        request: the flask Request object
    
    Returns:
        The board length value, an int
    
    Raises:
        ValueError: If request board length property is below 0
            or is not a valid int
    """
    board_length = request.args.get("board_length", '')
    if board_length != '':
        if int(board_length) < 1:
            raise ValueError("Provided board length must be above 0")
        return int(board_length)
    else:
        return None

def parse_move_request(request:Request):
    """ Gets the coordinates from the given request body

    Args:
        request: the flask Request object
    
    Returns:
        The coordinates (x,y) as a tuple of ints
    
    Raises:
        ValueError: If one or more coordinates is missing
            in the request body.
    """
    x = request.form.get("x", '')
    y = request.form.get("y", '')
    if (x is '' or y is ''):
        raise ValueError("No coordinates provided")
    return int(x), int(y)
    