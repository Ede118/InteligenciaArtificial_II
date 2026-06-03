import csv
import os

FILE_NAME = "fitness_history.csv"

def save_statistics(
    generation,
    best_fitness,
    mean_fitness,
    convergence_ratio
):

    file_exists = os.path.exists(FILE_NAME)

    with open(FILE_NAME, "a", newline="") as f:

        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "generation",
                "best_fitness",
                "mean_fitness",
                "convergence_ratio"
            ])

        writer.writerow([
            generation,
            best_fitness,
            mean_fitness,
            convergence_ratio
        ])