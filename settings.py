# Colors
BLACK = (0, 0, 0)
GRAY_900 = (40, 40, 40)
GRAY_500 = (127, 127, 127)
GRAY_300 = (170, 170, 170)
GRAY_100 = (220, 220, 220)
WHITE = (255, 255, 255)

# Setup
TITLE = "Neural Network Simulation"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
BG_COLOR = WHITE
MIN_DEPTH = 0
MAX_DEPTH = 30
FOCUS_DEPTH = 20
PARALAX_SCALE = 0.2  # Adjust this factor to control the speed of the parallax effect
PARALAX_EASING = 10.0  # Adjust this value to control the speed of easing (lower is slower)

# UI
UI_HEIGHT = 210

# Particles
PARTICLE_SPAWN_INTERVAL = 250
MAX_PARTICLE_COUNT = 20

# Neurons
NEURON_RADIUS = 10
NEURON_COLOR = BLACK
SPIKE_COLOR = WHITE
ACTION_POTENTIAL = 4
STARTING_TRAINING_RATE = 0.01
STARTING_TRAINING_DECAY_RATIO = 10 # between 30 and 5
# RC Circuit parameters
V_MAX = 5  # Maximum voltage in volts
V_THRESHOLD = 0.6 * V_MAX  # Threshold voltage for spiking
# RC parameters for resting state duration
R1 = 10  # Resistance in ohms
C1 = 0.1  # Capacitance in farads
TAU = R1 * C1  # Time constant

# Connections
CONNECTION_SEGMENTS = 20  # Number of segments for the line
CONNECTION_GROWTH_SPEED = 0.4  # Speed at which the line segments grow
CONNECTION_COLOR = BLACK
AXON_SPEED_FACTOR = 100 # multiplies the speed of the signal animation

# TRAINING SIM
TRAINING_WIDTH = 200
TRAINING_HEIGHT = 200