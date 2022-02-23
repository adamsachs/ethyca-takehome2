# How - to
## Prereqs
	- virtualenv is installed (and pyenv, if following verbatim)
	- linux or macOS
	- internet access (to download dependencies)

## Steps to run
	1. clone repo and cd into `ethyca-takehome2` 
	2. start a new python 3.7.0 venv: `pyenv virtualenv 3.7.0 my-new-venv` and then `pyenv activate my-new-venv`
	3. install dependencies `pip install -r requirements.txt`
	4. run `export FLASK_APP=server.py && python -m flask run`
		- this will run the web server (API backend) with your current terminal session. if you'd like to detach the server process from your session, consider using `screen` or something similar
	5. in another terminal session (assuming the server process is tied to your first session), you can activate the same pyenv as above, and then run the `test_http.py` script (`python test_http.py`) to execute some sample HTTP client calls against the live web server (using a python HTTP client)
		- the results of some of the calls are non-deterministic, given the "random" nature of the computer player
		- the calls will also get different responses if run against the same server process multiple times, as they are not idempotent. 
		- if you pass a "-t" flag (`python test_http.py -t`, it will run some basic checks/tests on the responses to ensure they are expected. this test will only work the first time the script is run a given server session, given that the calls are not idempotent.
	6. sample cURL calls are listed in the API documentation below. feel free to use those as a basis for some ad-hoc testing against the API
	7. `basic_ops_test.py` is a set of some unit tests that evaluate the backend functionality directly, i.e. bypassing the API layer. they don't require a running server process, and have deterministic results. you can execute the test suite by running `python basic_ops_test.py`

##  Dependencies
	- numpy
	- requests
	- flask

# API Specification

## Objects

### Game (API object):
	{
        "board_state": array[array[str]]
        "game_id": int,
        "game_state": str,
        "last_played": str,
        "started_time": str
    }

### Move (API object):
	{
        "board_state": array[array[str]],
        "move_id": int,
        "game_state": str,
        "last_moved": str,
        "timestamp": str,
    }

## Endpoints (and methods)

### POST /games
Starts (creates) a game
#### params
	- board_length: int (optional)
#### request
#### response:
	Game

#### example request
    curl -X POST  "localhost:5000/games"
#### example response
    {
        "board_state": "['.' '.' '.'], ['.' '.' '.'], ['.' '.' '.']",
        "game_id": 2,
        "game_state": "Game still ongoing",
        "last_played": null,
        "started_time": "2022-02-23 11:35:15.659000"
    }
    
### POST /moves
Makes a move at the specified coordinates on a specified game
#### params
	- game_id: int
#### request
    { "x" : int ,
      "y": int
    }
#### response:
	Game

#### example request
    curl -X POST "localhost:5000/moves?game_id=0" --data "x=1&y=1"
#### example response
    {
        "board_state": "['.' '.' '.'], ['.' 'X' 'O'], ['.' 'X' 'O']",
        "game_id": 0,
        "game_state": "Game still ongoing",
        "last_played": "O",
        "started_time": "2022-02-23 11:24:14.229983"
    }


### GET /moves
Gets the moves for a specified game
#### params
	- game_id: int
	- move ID: int (optional, if not specified, get all the moves in the game)
#### request
#### response:
	[Move]

#### example request
    curl -X GET "localhost:5000/moves?game_id=0"

#### example response
    [{
        "board_state": "['.' '.' '.'], ['.' '.' '.'], ['.' '.' '.']",
        "game_state": "Game still ongoing",
        "last_moved": null,
        "move_id": 0,
        "timestamp": "2022-02-23 11:24:14.235684"
    }, {
        "board_state": "['.' '.' '.'], ['.' '.' '.'], ['.' '.' 'X']",
        "game_state": "Game still ongoing",
        "last_moved": "X",
        "move_id": 1,
        "timestamp": "2022-02-23 11:24:14.262327"
    }, {
        "board_state": "['.' '.' '.'], ['.' 'O' '.'], ['.' '.' 'X']",
        "game_state": "Game still ongoing",
        "last_moved": "O",
        "move_id": 2,
        "timestamp": "2022-02-23 11:24:14.262456"
    }, {
        "board_state": "['.' '.' '.'], ['X' 'O' '.'], ['.' '.' 'X']",
        "game_state": "Game still ongoing",
        "last_moved": "X",
        "move_id": 3,
        "timestamp": "2022-02-23 11:24:14.268781"
    }, {
        "board_state": "['.' 'O' '.'], ['X' 'O' '.'], ['.' '.' 'X']",
        "game_state": "Game still ongoing",
        "last_moved": "O",
        "move_id": 4,
        "timestamp": "2022-02-23 11:24:14.268912"
    }]

### GET /games
Gets the specified game. If no game_id is specified, then get all the games.
#### params
	- game_id: int (optional, if not specified, get all the games)
#### request
#### response:
	[Game]

#### example request
    curl -X GET "localhost:5000/games"

#### example response
    [{
        "board_state": "['.' '.' '.'], ['.' 'O' '.'], ['.' 'X' '.']",
        "game_id": 0,
        "game_state": "Game still ongoing",
        "last_played": "O",
        "started_time": "2022-02-23 11:46:38.331059"
    }, {
        "board_state": "['O' '.' '.'], ['X' 'O' '.'], ['.' '.' 'X']",
        "game_id": 1,
        "game_state": "Game still ongoing",
        "last_played": "O",
        "started_time": "2022-02-23 11:46:38.336885"
    }]

# Background (Notes)
## Assumptions
I made the following assumptions:

	- no users or authentication
	- the server is set up to serve local clients, using the flask defaults of `127.0.0.1` as a hostname and `5000` as a port. this could easily be configured/parameterized if needed.
	- no persisted state after web server rebooots. this is a major limitation.
	- in highly concurrent environment, results may vary
	- the game ID is simply incremented as new games are created, e.g. first game created has game_id=0, second has game_id=1, etc.
	- the move ID is simply incremented as new moves are created within a game, e.g. the first move in a game has move_id=0, second has move_id=1, etc.
	- user is "X", computer is "O"

## Tradeoffs
	- I decided to focus on the functional requirements rather than operational requirements, e.g. scalability, persistence, etc. For isntance: 
		- I didn't use a persisted db. This would be a big limitation in terms of portability, durability, etc. but 
		- I wanted to write some test harnesses. They're not perfect, but at least gives some automated validation of functionality
		- I wanted to focus on documentation
		- I didn't focus a whole lot on performance - there are operations that could likely be optimized - but I generally tried to improve efficiency where I could.
		- I didn't focus on logistics of hosting and serving remote clients
	- I chose flask as a framework, mainly for the ease of bootstrapping.  I briefly considered django or http.server, but thought they were too heavyweight and lightweight, respectively. I'm not a python expert by any means, so this decision took a bit of both research and guesswork.

## Unique features
	- Users can play on any size board, not just 3x3. the user can specify the number of rows and columns (must be a square board).
	- Users can retrieve an individual game by ID
	- Users can retrieve an individual move by ID

## Notes
	- I spent a little over 4 hours
	- I spent a fair amount of time on documentation (~1 hour)
	- I spent more time than I probably should have on some silly things because of Python rustiness, e.g. trying to get array serialization right within JSON response, refreshing myself on some conventions, etc.