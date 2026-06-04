import random
import numpy as np

from Dinosaur import Dinosaur
from persistir_red import save_network
from statistics import save_statistics

def updateNetwork(population, generation):

    # ================= ORDENAR POR FITNESS =================
    population.sort(
        key=lambda d: d.score,
        reverse=True
    )

    best_fitness = population[0].score

    mean_fitness = np.mean(
        [d.score for d in population]
    )

    convergence_ratio = (
        mean_fitness / best_fitness
        if best_fitness > 0
        else 0
    )

    save_statistics(
        generation,
        best_fitness,
        mean_fitness,
        convergence_ratio
    )

    save_network(
        population[0].weights,
        population[0].biases
    )

    print("Mejor score:", population[0].score)

    # ================= SELECCIONAR MEJORES =================
    parents = select_fittest(population)

    new_population = []

    # ================= ELITISMO CONDICIONAL =================
    elite_count = 0

    if best_fitness >= 3000:
        elite_count = 1

    for elite in population[:elite_count]:

        elite_copy = Dinosaur(
            elite.id,
            elite.color,
            True
        )

        elite_copy.weights = [
            np.copy(w)
            for w in elite.weights
        ]

        elite_copy.biases = [
            np.copy(b)
            for b in elite.biases
        ]

        elite_copy.score = 0

        new_population.append(elite_copy)

    # ================= GENERAR HIJOS =================
    while len(new_population) < len(population):

        parent1, parent2 = random.sample(
            parents,
            2
        )

        child = evolve(
            parent1,
            parent2
        )

        new_population.append(child)

    # ================= REEMPLAZAR POBLACIÓN =================
    for i in range(len(population)):

        population[i].weights = [
            np.copy(w)
            for w in new_population[i].weights
        ]

        population[i].biases = [
            np.copy(b)
            for b in new_population[i].biases
        ]

        population[i].score = 0


def select_fittest(population):

    method="tournament"
    num_parents=None
    tournament_k= int(0.3 * len(population))

    if num_parents is None:
        num_parents = max(2, len(population) // 5)

    # ================= ELITISMO =================
    if method == "elitism":

        return population[:num_parents]

    # ================= TOURNAMENT =================
    elif method == "tournament":

        selected = []

        for _ in range(num_parents):

            participants = random.sample(
                population,
                tournament_k
            )

            participants.sort(
                key=lambda d: d.score,
                reverse=True
            )

            selected.append(participants[0])

        return selected

    # ================= ROULETTE =================
    elif method == "roulette":

        selected = []

        fitness_sum = sum(
            d.score for d in population
        )

        # evitar division por cero
        if fitness_sum == 0:
            return random.sample(
                population,
                num_parents
            )

        for _ in range(num_parents):

            pick = random.uniform(
                0,
                fitness_sum
            )

            current = 0

            for dino in population:

                current += dino.score

                if current >= pick:
                    selected.append(dino)
                    break

        return selected

    # ================= RANK =================
    elif method == "rank":

        ranked = sorted(
            population,
            key=lambda d: d.score
        )

        ranks = np.arange(
            1,
            len(ranked) + 1
        )

        probabilities = ranks / np.sum(ranks)

        selected = np.random.choice(
            ranked,
            size=num_parents,
            p=probabilities
        )

        return list(selected)

    else:
        raise ValueError(
            f"Método desconocido: {method}"
        )


def evolve(element1, element2):

    child = Dinosaur(
        element1.id,
        element1.color,
        True
    )

    mutation_rate = 0.2
    mutation_strength = 1.0

    child.weights = []
    child.biases = []

    # ================= CROSSOVER + MUTACIÓN =================

    # PESOS
    for W1, W2 in zip(element1.weights, element2.weights):

        # crossover 
        alpha = np.random.rand(*W1.shape)

        W_child = (
            alpha * W1
            + (1 - alpha) * W2
        )

        # mutación
        mutation_mask = (
            np.random.rand(*W_child.shape)
            < mutation_rate
        )

        mutations = (
            np.random.randn(*W_child.shape)
            * mutation_strength
        )

        W_child += mutation_mask * mutations

        child.weights.append(W_child)

    # BIASES
    for b1, b2 in zip(element1.biases, element2.biases):

        # crossover
        alpha = np.random.rand(*b1.shape)

        b_child = (
            alpha * b1
            + (1 - alpha) * b2
        )

        # mutación
        mutation_mask = (
            np.random.rand(*b_child.shape)
            < mutation_rate
        )

        mutations = (
            np.random.randn(*b_child.shape)
            * mutation_strength
        )

        b_child += mutation_mask * mutations

        child.biases.append(b_child)

    return child