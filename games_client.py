from __future__ import print_function
import argparse
from http.client import REQUEST_ENTITY_TOO_LARGE
from platform import platform
from queue import Empty
from urllib import request
import games_pb2 as games
import games_pb2_grpc as games_grpc
import grpc
import logging
import sys

args = {}

class ConfigError(Exception):
    pass

def setCustomLogger(name):
    formatter = logging.Formatter(fmt="%(asctime)s: %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(screen_handler)
    return logger

logger = setCustomLogger("KV")

def explain(msg):
  logger.info("%s" % msg)


def getGame(stub):
    game_key = int(input('''\n
                Input the game's key:\n
            Key:  '''))
    explain("Sending GET request to ...")
    response = stub.get(games.Key(key = game_key))
    
    if response.defined:
        print("'%s'='%s'" % (game_key, response.value))
    else:
        print("'%s': undefined" % game_key)



def putGame(stub):
    game_title = str(input('''\n
                Input the game's title:\n
            Title:  '''))
    game_price = float(input('''\n
                Input the game's price:\n
            Price:  '''))
    game_platform = str(input('''\n
                Input the game's platform:\n
            Platform:  '''))
    game_key = str(input('''\n
                Input the game's key:\n
            Key:  '''))

    game = games.Game(title=game_title, price=game_price, platform=game_platform)
    explain("Sending PUT request ...")
    game_to_add = games.NewGame(key=game_key, value=game)
    
    stub.put(game_to_add)
    print("Game added succesfully.")
    

def getKeys(stub):
    explain("Sending GET ALL KEYS request...")
    response = stub.getAllKeys(games.Void())
    print("----------------------")
    print("List of available keys:")
    for key in response.keys:
        print(key)

    print("----------------------")

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        
        def main_menu():
            stub = games_grpc.GameServiceStub(channel)
            option = int(input('''\n
            Choose an option:\n
            1 - Get\n
            2 - Put\n
            3 - GetAllKeys\n
            0 - Close\n
            Your option:  '''))
            print(option)
            if option == 1:
                getGame(stub=stub)
            elif option == 2:
                putGame(stub=stub)
            elif option == 3:
                getKeys(stub=stub)
            elif option == 0:
                exit()
            else:
                print("This is not an option. Please input a number from the listed options.\n")
                main_menu()
        while True:
            try:
                main_menu()
            except ValueError:
                print("Please input a number from the options.\n")


if __name__ == '__main__':
    logging.basicConfig()
    run()