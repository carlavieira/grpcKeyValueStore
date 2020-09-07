from concurrent import futures
import grpc
import logging
import sys

import games_pb2 as games
import games_pb2_grpc as games_grpc

fake_db = {
    1: {
        "title": "Final Fantasy",
        "price": 150.00,
        "platform": "Console"
    }
}

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

class GameServicer(games_grpc.GameServiceServicer):
    def get(self, request, context):
        key = request.key
        if key in fake_db.keys():
            # explain("Received GET request for key " + key + ": value = " + fake_db.get(key))
            
            game=fake_db.get(key)
            v = games.Value(value=game, defined=True)
            return v
            # return games.Value(value=fake_db.get(key), defined=True)
        else:
            explain("Received GET request for key "+ key +": value = undefined. Informed Key does not exists.")
            return games.Value(value=None, defined=False)

    def put(self, request, context):
        key = int(request.key)
        value = request.value
        print(value.title)
        fake_db[key] = value
        explain("received PUT request for key "+ str(key))
        #explain("New Game: Title "+value.title+" Price Platform "+value.pratform, value.price)
        return games.Void()

    def getAllKeys(self, request, context):
        explain("received GET ALL KEYS request")
        return games.StoredKeys(keys= fake_db.keys())


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    games_grpc.add_GameServiceServicer_to_server(GameServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Listening on 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    try:
        serve()
    except ConfigError as e:
        print("error:", e.args[0])