import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("fitness_history.csv")

plt.plot(
    df["generation"],
    df["best_fitness"],
    label="Best"
)

plt.plot(
    df["generation"],
    df["mean_fitness"],
    label="Mean"
)

plt.xlabel("Generation")
plt.ylabel("Fitness")
plt.grid(True)
plt.legend()

plt.show()

plt.figure()

plt.plot(
    df["generation"],
    df["convergence_ratio"]
)

plt.xlabel("Generation")
plt.ylabel("Mean / Best")
plt.grid(True)

plt.show()