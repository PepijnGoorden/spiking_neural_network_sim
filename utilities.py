import pygame
from settings import *
from globals import *
from neuron import *

def initial_setup():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
    clock = pygame.time.Clock()
    is_running = True
    return screen, clock, is_running

# Global variables for mouse offset
current_mouse_offset = pygame.math.Vector2(0, 0)
target_mouse_offset = pygame.math.Vector2(0, 0)

def smoothstep(edge0, edge1, x):
    x = max(0, min((x - edge0) / (edge1 - edge0), 1))
    return x * x * (3 - 2 * x)

def update_mouse_offset(dt, mouse_pos):
    global current_mouse_offset, target_mouse_offset
    screen_center = pygame.math.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
    target_mouse_offset = pygame.math.Vector2(mouse_pos) - screen_center
    
    easing_speed = PARALAX_EASING  # Adjust this value in settings.py to control the speed of easing
    t = smoothstep(0, 1, easing_speed * dt)
    
    current_mouse_offset += (target_mouse_offset - current_mouse_offset) * t

# Neuron utility functions
dragging = False
from_neuron = None

def get_neuron_at_pos(pos):
    for neuron in neurons:
        if neuron.is_clicked(pos, current_mouse_offset):
            return neuron
    return None

def add_neuron(pos, neuron_type=NeuronType.REGULAR):
    parallax_offset = current_mouse_offset * (1 - (FOCUS_DEPTH / MAX_DEPTH)) * PARALAX_SCALE
    adjusted_pos = (pos[0] - parallax_offset.x, pos[1] - parallax_offset.y)
    neurons.append(Neuron(*adjusted_pos, neuron_type))

def remove_neuron(neuron):
    neuron.remove_all_connections()
    neurons.remove(neuron)