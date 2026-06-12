import pandas as pd
import matplotlib.pyplot as plt

files = {
    "16": {
        20: "fitness_history_layer_16_pob_20.csv",
        100: "fitness_history_layer_16_pob_100.csv",
        50: "fitness_history_layer_16_pob_50.csv"
    },
    "16-16": {
        20: "fitness_history_layer_16_16_pob_20.csv",
        100: "fitness_history_layer_16_16_pob_100.csv",
        50: "fitness_history_layer_16_16_pob_50.csv"
    },
    "16-16-16": {
        20: "fitness_history_layer_16_16_16_pob_20.csv",
        100: "fitness_history_layer_16_16_16_pob_100.csv",
        50: "fitness_history_layer_16_16_16_pob_50.csv"
    }
}

for population in [20, 50, 100]:

    plt.figure(figsize=(10, 6))

    for layer_name in files:

        df = pd.read_csv(files[layer_name][population])

        plt.plot(
            df["generation"],
            df["best_fitness"],
            label=f"Layer {layer_name}"
        )

    plt.title(f"Best Fitness - Population {population}")
    plt.xlabel("Generation")
    plt.ylabel("Best Fitness")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.show()