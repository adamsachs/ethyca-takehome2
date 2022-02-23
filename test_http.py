from flask import Response
import requests
import sys

HOSTNAME = "localhost"
PORT = "5000"
BASE_URL = f"http://{HOSTNAME}:{PORT}"

def test_http(raise_errors: bool = False):
    check_response(test_games_post(), "\"game_id\": 0", raise_errors=raise_errors)
    check_response(test_games_post(), "\"game_id\": 1", raise_errors=raise_errors)
    check_response(test_games_get(0), "\"game_id\": 0", raise_errors=raise_errors)
    check_response(test_games_get(1), "\"game_id\": 1", raise_errors=raise_errors)
    r = test_games_get()
    check_response(r, "\"game_id\": 0", raise_errors=raise_errors)
    check_response(r, "\"game_id\": 1", raise_errors=raise_errors)
    r = test_moves_post(0, 1, 2)
    check_response(r, "\"game_id\": 0", raise_errors=raise_errors)
    check_response(r, "'X", raise_errors=raise_errors)
    r = test_moves_post(1, 2, 2)
    check_response(r, "\"game_id\": 1", raise_errors=raise_errors)
    check_response(r, "'X'", raise_errors=raise_errors)
    r = test_moves_post(1, 0, 1)
    #this may return an error, if we happen to go where computer went
    if "Invalid" in r.text: 
        r = test_moves_post(1, 1, 2)
    r = test_moves_get(0)
    check_response(r, "\"move_id\": 0", raise_errors=raise_errors)
    check_response(r, "\"move_id\": 1", raise_errors=raise_errors)
    check_response(r, "\"move_id\": 2", raise_errors=raise_errors)
    r = test_moves_get(1)
    check_response(r, "\"move_id\": 0", raise_errors=raise_errors)
    check_response(r, "\"move_id\": 1", raise_errors=raise_errors)
    check_response(r, "\"move_id\": 3", raise_errors=raise_errors)
    r  = test_moves_get(1, 1)
    check_response(r, "\"move_id\": 1", raise_errors=raise_errors)
    r = test_moves_get(0, 1)
    check_response(r, "\"move_id\": 1", raise_errors=raise_errors)

def test_games_get(game_id: int=None):
    url = BASE_URL + "/games"
    if game_id is not None:
        r = get(url, {"game_id": game_id})
    else:
        r = get(url)
    return response_handler(r)

def  test_games_post():
    url = BASE_URL + "/games"
    r = post(url)
    return response_handler(r)

def test_moves_post(game_id, x, y):
    url = BASE_URL + "/moves"
    r = post(url, {"game_id": game_id}, {"x": x, "y": y})
    return response_handler(r)

def test_moves_get(game_id, move_id=None):
    url = BASE_URL + "/moves"
    if move_id is None:
        r = get(url, {"game_id" : game_id})
    else:
        r = get(url, {"game_id" : game_id, "move_id" : move_id})
    return response_handler(r)

def get(url: str, params: dict = {}) -> requests.Response: 
    print (f"GET {url}...")
    print(f"params: {params}")
    return requests.get(url, params=params)

def post(url: str, params: dict = {}, data: dict = {}) -> requests.Response: 
    print (f"POST {url}...")
    print(f"params: {params}")
    print(f"data: {data}")
    return requests.post(url, params=params, data=data)

def response_handler(r: Response):
    print(f"\n----BEGIN RESPONSE----\n{r.text}\n----END RESPONSE----\n")
    return r

# basic check for string in response
def check_response(r: Response, str_to_check: str, raise_errors):
    if str_to_check not in r.text and raise_errors:
        raise ValueError(f"Did not find {str_to_check} in response!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and (sys.argv[1] == "-t"):
        test_http(raise_errors=True)
    else:
        test_http(raise_errors=False)