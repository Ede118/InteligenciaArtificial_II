import numpy as np

class NeuralNetwork:
    def __init__(self):
        self.initialize()

    def initialize(self):
        # ======================== INITIALIZE NETWORK WEIGTHS AND BIASES =============================
        self.input_layer_size: int = 8
        self.output_layer_size: int = 3

        self.hidden_layers: list[int] = [16]
        self.layers: list[int] = (
            [self.input_layer_size] 
            + self.hidden_layers 
            + [self.output_layer_size]
        )

        self.weights: list[np.ndarray] = []
        self.biases: list[np.ndarray] = []

        for i in range(len(self.layers) - 1):
            rows = self.layers[i+1]
            cols = self.layers[i]

            W = np.random.uniform(-1, 1, (rows, cols))
            b = np.random.uniform(-0.9, 0.9, (rows, 1))

            self.weights.append(W)
            self.biases.append(b)
        # ============================================================================================

    def think(self, y_dino, x_obstacle, is_bird, is_large, is_small, t_collision, y_obstacle, obstacle_width):
        # ======================== PROCESS INFORMATION SENSED TO ACT =============================
        print(f"y_dino: {y_dino}, x_obstacle: {x_obstacle}, is_bird: {is_bird}, is_large: {is_large}, is_small: {is_small}, t_collision: {t_collision}, y_obstacle: {y_obstacle}, obstacle_width: {obstacle_width}")
        input = np.array(
            [[y_dino], 
            [x_obstacle], 
            [is_bird], 
            [is_large], 
            [is_small],
            [t_collision],
            [y_obstacle],
            [obstacle_width]]
        )

        a = input

        # FORWARD PROPAGATION
        for W, b in zip(self.weights, self.biases):

            z = np.dot(W, a) + b
            a = self.sigmoid(z)

        result = np.argmax(a)
        # ========================================================================================
        return self.act(result)

    def act(self, output):
        # ======================== USE THE ACTIVATION FUNCTION TO ACT =============================
        action = output


        # =========================================================================================
        if (action == 0):
            return "JUMP"
        elif (action == 1):
            return "DUCK"
        elif (action == 2):
            return "RUN"
    
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
