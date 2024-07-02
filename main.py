import pygame
import sys
from random import randint, uniform
from settings import *
from utilities import *
from particles import *
from neuron import *

# Initialize Pygame
screen, clock, is_running = initial_setup()

# Setup particle timer
particle_timer_event = setup_particle_timer()

# Spawn initial particles
for _ in range(MAX_PARTICLE_COUNT):
    spawn_background_particle(False)

# Main loop
while is_running:
    dt = clock.tick(60) / 1000.0  # Delta time in seconds
    mouse_pos = pygame.mouse.get_pos()
    update_mouse_offset(dt, mouse_pos)
    #print(len(neurons))
    #print(len(particle_group))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        elif event.type == pygame.VIDEORESIZE:
            window_size = (event.w, event.h)
            screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        elif event.type == particle_timer_event:
            spawn_background_particle(True)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                neuron = get_neuron_at_pos(event.pos)
                if neuron:
                    dragging = True
                    from_neuron = neuron
                    start_pos = (from_neuron.x, from_neuron.y)
                    end_pos = event.pos
                    rope, segment_length = create_rope(start_pos, end_pos, num_segments)
                else:
                    add_neuron(event.pos)
            elif event.button == 3:  # Right click
                neuron = get_neuron_at_pos(event.pos)
                if neuron:
                    remove_neuron(neuron)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and dragging:  # Left click release
                dragging = False
                to_neuron = get_neuron_at_pos(event.pos)
                if to_neuron and from_neuron and to_neuron != from_neuron:
                    from_neuron.add_connection(to_neuron)
                from_neuron = None
                rope = None

    # Check if mouse hovers a neuron
    hovered_neuron = get_neuron_at_pos(pygame.mouse.get_pos())

    # Update neurons
    for neuron in neurons:
        if hovered_neuron == neuron:
            neuron.external_stimulation += 10
        neuron.update_neuron(dt)

    # Update rope if dragging
    if dragging and from_neuron:
        start_pos = (from_neuron.x, from_neuron.y)
        end_pos = mouse_pos
        update_rope(rope, start_pos, end_pos, dt, segment_length, current_mouse_offset)

    # Clear the screen
    screen.fill(BG_COLOR)

    # Update and draw particles
    update_and_draw_particles(screen, dt)

    # Draw neurons
    for neuron in neurons:
        neuron.draw(screen, current_mouse_offset)
        neuron.draw_connections(screen, current_mouse_offset)

    # Draw the rope if dragging
    if dragging and rope:
        draw_rope(screen, rope)

    # update the display
    pygame.display.flip()

    # update time
    clock.tick(60)

pygame.quit()
sys.exit()