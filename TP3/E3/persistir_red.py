import pickle
import os

FILE_NAME = "best_dino.pkl"

def save_network(weights, biases):

    data = {
        "weights": weights,
        "biases": biases
    }

    with open(FILE_NAME, "wb") as f:
        pickle.dump(data, f)


def load_network():

    if not os.path.exists(FILE_NAME):
        return None

    with open(FILE_NAME, "rb") as f:
        return pickle.load(f)