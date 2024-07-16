import pygame
import pygame_gui
import sys
from random import randint, uniform
from settings import *
from utilities import *
from particles import *
from neuron import *
from training_sim import *
import globals

# Initialize Pygame
window_size, screen, clock, is_running = initial_setup()

# Create a UI Manager
ui_manager = pygame_gui.UIManager(window_size, 'bw_theme.json')

# Calculate positions
slider_width = 150
slider_height = 20
textbox_width = 50
textbox_height = 20
margin_left = 20
margin_bottom = 20

# Create a label
label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((margin_left, window_size[1] - margin_bottom - slider_height - 30), (200, 30)),
    text="Neuron Training Rate",
    manager=ui_manager,
    object_id=pygame_gui.core.ObjectID(class_id="@labels", object_id="#neuron_rate_label")
)

# Create a slider
slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((margin_left, window_size[1] - margin_bottom - slider_height), (slider_width, slider_height)),
    start_value=globals.neuron_training_rate,
    value_range=(0.001, 0.1),
    manager=ui_manager
)

# Create a textbox
textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((margin_left + slider_width + 10, window_size[1] - margin_bottom - textbox_height), (textbox_width, textbox_height)),
    manager=ui_manager
)
textbox.set_text(f"{slider.get_current_value():.3f}")

# Setup particle timer
particle_timer_event = setup_particle_timer()

# Spawn initial particles
for _ in range(MAX_PARTICLE_COUNT):
    spawn_background_particle(False)

input1_position = pygame.math.Vector2(150 + NEURON_RADIUS, WINDOW_HEIGHT / 2)
input2_position = pygame.math.Vector2(150 + NEURON_RADIUS, (WINDOW_HEIGHT / 2) + NEURON_RADIUS + 50)
output_position = pygame.math.Vector2(WINDOW_WIDTH - 150 - NEURON_RADIUS, WINDOW_HEIGHT / 2)
add_neuron(input1_position, NeuronType.POSITION_INPUT)
add_neuron(input2_position, NeuronType.VELOCITY_INPUT)
add_neuron(output_position, NeuronType.OUTPUT)

# Create the training sim
TRAINING_WIDTH, TRAINING_HEIGHT = 200, 200
training_sim = create_training_sim(TRAINING_WIDTH, TRAINING_HEIGHT)
training_surface = pygame.Surface((TRAINING_WIDTH, TRAINING_HEIGHT))

# Main loop
while is_running:
    dt = clock.tick(60) / 1000.0  # Delta time in seconds
    mouse_pos = pygame.mouse.get_pos()
    update_mouse_offset(dt, mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        elif event.type == pygame.VIDEORESIZE:
            window_size = (event.w, event.h)
            screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        elif event.type == particle_timer_event:
            spawn_background_particle(True)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and event.pos[1] < WINDOW_HEIGHT - UI_HEIGHT:  # Left click
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
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                neuron_info = not neuron_info
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == slider:
                globals.neuron_training_rate = event.value
                textbox.set_text(f"{globals.neuron_training_rate:.3f}")
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == textbox:
                try:
                    new_value = float(event.text)
                    if 0.001 <= new_value <= 0.1:
                        slider.set_current_value(new_value)
                    else:
                        textbox.set_text(f"{slider.get_current_value():.3f}")
                except ValueError:
                    textbox.set_text(f"{slider.get_current_value():.3f}")

        ui_manager.process_events(event)
    
    ui_manager.update(dt)

    # Check if mouse hovers a neuron
    hovered_neuron = get_neuron_at_pos(pygame.mouse.get_pos())

    # Update neurons
    for neuron in neurons:
        # Stimulate hovered neuron, if it is not firing
        if hovered_neuron == neuron:
            if not neuron.is_firing:
                neuron.membrane_potential += 1
        if neuron.neuron_type == NeuronType.OUTPUT:
            if neuron.is_firing:
                is_thrusting = True
            else:
                is_thrusting = False
        if neuron.neuron_type == NeuronType.POSITION_INPUT:
            if not neuron.is_firing:
                position_low_input, position_high_input, velocity_input = stimulate_neuron_with_game_output(training_sim.position_data, training_sim.velocity)
                neuron.membrane_potential += position_low_input
        if neuron.neuron_type == NeuronType.VELOCITY_INPUT:
            if not neuron.is_firing:
                position_low_input, position_high_input, velocity_input = stimulate_neuron_with_game_output(training_sim.position_data, training_sim.velocity)
                neuron.membrane_potential += velocity_input
                #print(f"Velocity: {velocity_input}")
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
        neuron.draw_neuron(screen, current_mouse_offset, neuron_info)

    # Draw the rope if dragging
    if dragging and rope:
        draw_rope(screen, rope)

    # Draw vignette on top of everything
    screen.blit(vignette, (0, 0))

    # Draw a UI base
    ui_base = pygame.Rect(0, WINDOW_HEIGHT - UI_HEIGHT, WINDOW_WIDTH, UI_HEIGHT)
    pygame.draw.rect(screen, GRAY_300, ui_base)

    # Update and draw training sim
    training_sim.update(is_thrusting)
    training_sim.draw(training_surface)

    ui_manager.draw_ui(screen)

    # Draw training sim to the bottom right corner of the main screen
    screen.blit(training_surface, (WINDOW_WIDTH - TRAINING_WIDTH, WINDOW_HEIGHT - TRAINING_HEIGHT))

    # update the display
    pygame.display.flip()

    # update time
    clock.tick(60)

pygame.quit()
sys.exit()