import numpy as np

def normalize(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val)

def scalar_to_spikes(scalar_value, max_rate, duration, dt):
    scalar_value = np.clip(scalar_value, 0, 1)
    firing_rate = scalar_value * max_rate
    num_steps = int(duration / dt)
    spikes = np.random.rand(num_steps) < (firing_rate * dt)
    return spikes

# Given weights and biases
weights = [1.3, 1.2, 1.3, 1.2, -1.3, 0, -1.5, 0.8, 0]
min_weight, max_weight = -1.5, 1.5

# Normalize weights
normalized_weights = [normalize(w, min_weight, max_weight) for w in weights]

# Parameters for spike train
max_rate = 200  # Hz
duration = 1.0  # second
dt = 0.001      # second (1 ms)

# Convert normalized weights to spike trains
spike_trains = [scalar_to_spikes(w, max_rate, duration, dt) for w in normalized_weights]

# Display the spike trains
for i, spikes in enumerate(spike_trains):
    readable_spikes = ''.join(['|' if spike else ' ' for spike in spikes])
    print(f"Spike train for weight {i + 1}: {readable_spikes}")