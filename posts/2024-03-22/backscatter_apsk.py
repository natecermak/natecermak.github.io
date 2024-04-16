#!/usr/bin/env python3

from itertools import combinations
import warnings

import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize


frequency = 1e6
w0 = 2 * np.pi * frequency
L_inductor = 75e-6
R_inductor = 13
Z_inductor = R_inductor + 1j * w0 * L_inductor


def powerset(s):
    x = len(s)
    masks = [1 << i for i in range(x)]
    for i in range(1 << x):
        yield [ss for mask, ss in zip(masks, s) if i & mask]


def calculate_parallel_impedances(Z_set):
    return 1.0 / np.sum([1 / z for z in Z_set])


def get_all_possible_parallel_impedances(Z_set):
    return [calculate_parallel_impedances(Z_subset) for Z_subset in powerset(Z_set)]


def get_all_possible_series_impedances(Z_set):
    return [np.sum(Z_subset) for Z_subset in powerset(Z_set)]


def impedance_to_modulation(Z_parallel, Z_inductor):
    j = np.where(np.isinf(Z_parallel))[0]
    M = (Z_parallel + np.conjugate(Z_inductor)) / (Z_parallel + np.abs(Z_inductor) ** 2 / (2 * np.real(Z_inductor)))
    if len(j) > 0:
        M[j] = 1  # inf/inf --> 1
    return M


## find optimal loads such that any parallel combination has the maximally well-separated set of symbols possible


def get_all_pair_distances(points):
    distances = [abs(points[i] - points[j]) for i in range(len(points)) for j in range(i + 1, len(points))]
    return distances


def real_to_complex(x):
    """Because optimizer doesn't optimize over complex plane, convert
    real n-element array to complex (n/2)-element array"""
    return np.array([x[i] + 1j * x[i + 1] for i in range(0, len(x), 2)])


def objective(parameters):
    Z_individual = real_to_complex(parameters)
    Z_parallel = get_all_possible_parallel_impedances(Z_individual)
    # Z_series = get_all_possible_series_impedances(Z_individual)
    modulations = impedance_to_modulation(Z_parallel, Z_inductor)
    distances = get_all_pair_distances(modulations)
    # return np.sum( (1 / np.array(distances)**2))  # alternative distance metric
    return -np.min(distances) * 1_000_000


n_bits = 4

# repeat fit from 100 random starting configurations, take the best one
best_fit = None
for i in range(100):
    print(".", end="", flush=True)
    x0 = np.vstack([10 ** (5 * np.random.rand(4)), -1 * 10 ** (5 * np.random.rand(4))]).T.flatten()
    # bounds specify real part must be positive, reactance must be negative (capacitive)
    bounds = [(0, None), (None, 0)] * n_bits
    warnings.filterwarnings("ignore")
    fit = scipy.optimize.minimize(fun=objective, x0=x0, bounds=bounds)

    if best_fit is None or fit.fun < best_fit.fun:
        best_fit = fit

# plot the results
fit = best_fit
Z_single = real_to_complex(fit.x)
Z_set = get_all_possible_parallel_impedances(Z_single)
M_set = impedance_to_modulation(Z_set, Z_inductor)
M_single = impedance_to_modulation(Z_single, Z_inductor)

plt.figure()
plt.scatter(np.real(M_set), np.imag(M_set))
plt.scatter(np.real(M_single), np.imag(M_single))
plt.xlabel("Re(M)")
plt.ylabel("Im(M)")
plt.xlim([-0.04, 1])
plt.axhline(0, color="gray")
plt.axvline(0, color="gray")
plt.gca().add_patch(plt.Circle((0.5, 0), 0.5, fill=False, linestyle=(0, (1, 10))))

C = [-1 / (w0 * np.imag(z)) for z in Z_single]

print(f"Individual subcircuits: {np.round(Z_single)}")
print(f"Individual subcircuits (R&C): R={np.round(np.real(Z_single))}, C={C}")

print(f"min distance: {-fit.fun/1e6}")

plt.show()
