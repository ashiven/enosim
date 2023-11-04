import math

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

mu = 0
variance = 1
sigma = math.sqrt(variance)
x = np.linspace(mu - 3 * sigma, mu + 3 * sigma, 100)


for i in range(-3, 4):
    if i == 0:
        continue
    plt.axvline(mu + i * sigma, color="r", linestyle="--")

for i in range(-3, 4):
    if i == 0:
        continue
    plt.text(
        mu + (i - 1 if i > 0 else i) * sigma + sigma / 2, 0.1, f"{i}σ", ha="center"
    )

plt.plot(x, stats.norm.pdf(x, mu, sigma))
plt.show()
