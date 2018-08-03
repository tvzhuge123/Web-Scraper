# Author: Yan Zhang
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, gamma, lognorm, chisquare


# Read data
df = pd.read_csv('history_data.csv', header=None, names=['Page', 'Step'])


# Analysis
sample_size = df['Step'].shape[0]
percent_success = df[df['Step'] > 0].shape[0] / sample_size * 100
percent_deadend = df[df['Step'] == -3].shape[0] / sample_size * 100
percent_loop = df[df['Step'] == -2].shape[0] / sample_size * 100
percent_maxtry = df[df['Step'] == -1].shape[0] / sample_size * 100

print("Total number of pages:", sample_size)
print("Percentage of pages that reach Philosophy: %.2f%%" % percent_success)
print("Percentage of pages that get into dead end: %.2f%%" % percent_deadend)
print("Percentage of pages that get into infinite loop: %.2f%%" % percent_loop)
print("Percentage of pages that have not reached Philosophy under 1000 tries: %.2f%%" % percent_maxtry)

df = df['Step'][df['Step'] > 0]
x = np.linspace(0,35,500)


# Fit normal distribution
mu, sigma = norm.fit(df)
y_norm = norm.pdf(x, mu, sigma)

# Fit gamma distribution
shape, loc, scale = gamma.fit(df, floc=0)
y_gamma = gamma.pdf(x, shape, loc, scale)

# Calculate bins
n, bins, patches = plt.hist(df, 10, normed=True)

# Chi square goodness of fit test - normal distribution
sample_freq, expect_freq = [], []
for i in range(len(bins)-1):
    sample_freq.append(df[(df >= bins[i]) & (df < bins[i+1])].shape[0])
    expect_freq.append((norm.cdf(bins[i+1], mu, sigma) - norm.cdf(bins[i], mu, sigma)) * sample_size)
print("Gaussian:", chisquare(sample_freq, expect_freq))

# Chi square goodness of fit test - gamma distribution
sample_freq, expect_freq = [], []
for i in range(len(bins)-1):
    sample_freq.append(df[(df >= bins[i]) & (df < bins[i+1])].shape[0])
    expect_freq.append((gamma.cdf(bins[i+1], shape, loc, scale) - gamma.cdf(bins[i], shape, loc, scale)) * sample_size)
# print(expect_freq)
# print(sample_freq)
print("Gamma:", chisquare(sample_freq, expect_freq))

# Plot Histogram with fitted lines
plt.plot(x, y_norm, label=r'$Gaussian\ (\mu=%.2f,\ \sigma=%.2f)$' % (mu, sigma))
plt.plot(x, y_gamma, label=r'$Gamma\ (k=%.2f,\ \theta=%.2f)$' % (shape, scale))
plt.xlabel('Path lengths')
plt.ylabel('Probability')
plt.title('Histogram')
plt.legend()
plt.grid(True)
plt.show()
