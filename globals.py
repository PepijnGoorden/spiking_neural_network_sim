import pygame
from settings import *

# Setup
window_size = (WINDOW_WIDTH, WINDOW_HEIGHT)

# UI
neuron_training_rate = STARTING_TRAINING_RATE
neuron_training_decay_ratio = STARTING_TRAINING_DECAY_RATIO
neuron_training_decay = STARTING_TRAINING_RATE / STARTING_TRAINING_DECAY_RATIO