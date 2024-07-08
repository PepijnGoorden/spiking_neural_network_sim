import pygame
import math
from settings import *
import os

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

# Neuron list
neurons = []

# Neuron UI
global neuron_info
neuron_info = True

# Load neuron sprites
neurons_sprite_dir = "resources/img/neurons"
connection_overlay_path = os.path.join(neurons_sprite_dir, f"connection_overlay.png")
connection_overlay_sprite = pygame.image.load(connection_overlay_path).convert_alpha()

class Connection:
    def __init__(self, neuron, target_neuron):
        self.connected_from = neuron
        self.connected_to = target_neuron
        self.segments = CONNECTION_SEGMENTS
        self.animation_progress = 0
        self.is_animating = False

class Neuron:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.connections_to = []  # Connections to other neurons
        self.connections_from = []  # Neurons that connect to this neuron
        self.is_firing = False # Is the neuron in the active state?
        self.membrane_potential = 0  # Stimulation level / membrane potential
        self.resting_time_constant = R1 * C1  # Time constant
        self.postsynaptic_action_potentials = 0 # Accumulation of stimulation signals
        self.weight = 0.25
        self.trainig_factor = 0.01

    #Neuron Behavior
    def fire(self):
        self.is_firing = True
        for connection in self.connections_to:
            connection.is_animating = True
            connection.animation_progress = 0  # Reset animation progress when firing
            self.membrane_potential = 0  # Reset stimulation level (membrane_potential) after firing

    def propogate_action_potentials(self, dt):
        all_animations_finished = True
        for connection in self.connections_to:
            if connection.is_animating:
                connection.animation_progress += dt * AXON_SPEED_FACTOR
                # When axon signal animation ends
                if connection.animation_progress >= connection.segments:
                    connection.is_animating = False
                    self.weight += self.trainig_factor # Update Neuron Weight
                    connection.connected_to.postsynaptic_action_potentials += 25 * self.weight # Stimulate receiving neuron
                else:
                    all_animations_finished = False
        
        if all_animations_finished:
            self.is_firing = False

    # DRAW and UPDATE events
    def update_neuron(self, dt):
        if self.is_firing: # If neuron is in active state
            self.propogate_action_potentials(dt)            

        else: # If neuron is in resting state
            # Apply external stimulation
            if self.postsynaptic_action_potentials > 0:
                self.membrane_potential += (V_MAX - self.membrane_potential) * (self.postsynaptic_action_potentials * dt / self.resting_time_constant)
            
            # Decay resting voltage and weight
            self.membrane_potential *= math.exp(-dt / self.resting_time_constant)
            if self.weight > 0.1:
                self.weight -= self.trainig_factor / 100
            
            # Check if threshold is reached
            if self.membrane_potential >= V_THRESHOLD:
                self.fire()
        
        # Reset external stimulation at the end of each update
        self.postsynaptic_action_potentials = 0

    def draw_neuron(self, screen, current_mouse_offset, neuron_info):
        # Calculate parallax offset assuming neurons are always at the focus depth
        parallax_offset = current_mouse_offset * (1 - (FOCUS_DEPTH / MAX_DEPTH)) * PARALAX_SCALE
        screen_pos = (int(self.x + parallax_offset.x), int(self.y + parallax_offset.y))

        # Draw the components
        self.draw_self(screen, screen_pos)
        self. draw_connections(screen, parallax_offset)
        self.draw_info(screen, screen_pos, neuron_info)

    def draw_self(self, screen, screen_pos):
        # Draw the neuron
        color = SPIKE_COLOR if self.is_firing else NEURON_COLOR #Change SPIKE_COLOR in dark mode
        pygame.draw.circle(screen, color, screen_pos, NEURON_RADIUS)

    def draw_info(self, screen, screen_pos, neuron_info):
        # Draw membrane_potential and weight text
        if neuron_info:
            font = pygame.font.Font(None, 24)  # You may need to adjust the font size
            text = font.render(f"{self.membrane_potential:.2f}", True, (0, 0, 0))
            text_pos = (screen_pos[0] - (NEURON_RADIUS * 1.5), screen_pos[1] + NEURON_RADIUS + 5)  # Position under the neuron
            screen.blit(text, text_pos)
            text = font.render(f"{self.weight:.2f}", True, (0, 0, 0))
            text_pos = (screen_pos[0] - (NEURON_RADIUS * 1.5), screen_pos[1] + NEURON_RADIUS + 20)  # Position under the neuron
            screen.blit(text, text_pos)

    def draw_connections(self, screen, parallax_offset):
        # Draw the connections
        for connection in self.connections_to:
            # Apply the parallax offset to the starting position, same as screen_pos in main draw_neuron(), but because we need a offset for the ending position aswell, doing them both here makes it clearer.
            from_pos = pygame.math.Vector2(
                int(connection.connected_from.x + parallax_offset.x),
                int(connection.connected_from.y + parallax_offset.y)
            )
            # Apply the parallax offset to the ending position,
            to_pos = pygame.math.Vector2(
                int(connection.connected_to.x + parallax_offset.x),
                int(connection.connected_to.y + parallax_offset.y)
            )

            # Determine the segment length by getting the distance between to and from and deviding them by the number of segments
            segment_vector = (to_pos - from_pos) / connection.segments
            
            # Loop through all segments
            for i in range(connection.segments):
                # Determen where the segment starts and ends
                start = from_pos + segment_vector * i
                end = from_pos + segment_vector * (i + 1)
                
                # Determine line width based on animation state
                if connection.is_animating:
                    progress = connection.animation_progress - i
                    if 0 <= progress < 1:
                        width = 4
                        color = CONNECTION_COLOR #in dark mode, this could be awesome to light the signal
                    else:
                        width = 2
                        color = CONNECTION_COLOR
                else:
                    width = 2
                    color = CONNECTION_COLOR
                # Draw the segment
                pygame.draw.line(screen, color, start, end, width)

            # Drawing the pointy overlay sprite at the start of the connection
            # Calculate rotation angle
            angle = math.degrees(math.atan2(to_pos.y - from_pos.y, to_pos.x - from_pos.x))
            rotated_connection_overlay = pygame.transform.rotate(connection_overlay_sprite, -angle)

            # Calculate the offset (half the sprite width is 12.5)
            half_sprite_width = 12.5
            angle_radians = math.radians(angle)
            offset_x = half_sprite_width * math.cos(angle_radians)
            offset_y = half_sprite_width * math.sin(angle_radians)

            # Calculate the new position with the offset applied
            offset_pos = (from_pos.x + offset_x, from_pos.y + offset_y)

            # Draw the rotated overlay sprite at the new position
            first_segment = rotated_connection_overlay.get_rect(center=offset_pos)
            screen.blit(rotated_connection_overlay, first_segment)

    # NEURON UTILITIES        
    def is_clicked(self, pos, current_mouse_offset):
        # Calculate parallax offset assuming neurons are always at the focus depth
        parallax_offset = current_mouse_offset * (1 - (FOCUS_DEPTH / MAX_DEPTH)) * PARALAX_SCALE
        adjusted_x = self.x + parallax_offset.x
        adjusted_y = self.y + parallax_offset.y
        return (adjusted_x - pos[0])**2 + (adjusted_y - pos[1])**2 < NEURON_RADIUS**2

    def add_connection(self, target_neuron):
        if not any(connection.connected_to == target_neuron for connection in self.connections_to):
            new_connection = Connection(self, target_neuron)
            self.connections_to.append(new_connection)
            target_neuron.connections_from.append(self)

    def remove_connection(self, target_neuron):
        self.connections_to = [connection for connection in self.connections_to if connection.connected_to != target_neuron]
        target_neuron.connections_from.remove(self)

    def remove_all_connections(self):
        for connection in self.connections_to[:]:
            self.remove_connection(connection.connected_to)
        for neuron in self.connections_from[:]:
            neuron.remove_connection(self)

# Rope stuff
num_segments = CONNECTION_SEGMENTS
rope = None

class Point:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.old_pos = pygame.math.Vector2(x, y)
        self.acc = pygame.math.Vector2(0, 0)

    def update(self, dt, damping=0.1):
        velocity = (self.pos - self.old_pos) * damping
        self.old_pos = pygame.math.Vector2(self.pos)
        self.pos += velocity + self.acc * dt * dt
        self.acc *= 0

    def apply_force(self, force):
        self.acc += force

    def constrain(self, other, length):
        diff = self.pos - other.pos
        dist = diff.length()
        if dist > length:
            diff_scale = (dist - length) / dist
            correction = diff * diff_scale * 0.5
            self.pos -= correction
            other.pos += correction

def create_rope(start_pos, end_pos, num_segments):
    rope = []
    segment_length = (pygame.math.Vector2(end_pos) - pygame.math.Vector2(start_pos)).length() / num_segments
    for i in range(num_segments + 1):
        t = i / num_segments
        pos = pygame.math.Vector2(start_pos).lerp(pygame.math.Vector2(end_pos), t)
        rope.append(Point(pos.x, pos.y))
    return rope, segment_length

def update_rope(rope, start_pos, end_pos, dt, segment_length, current_mouse_offset):
    parallax_offset = current_mouse_offset * (1 - (FOCUS_DEPTH / MAX_DEPTH)) * PARALAX_SCALE
    
    for point in rope:
        point.apply_force(pygame.math.Vector2(0, 50))  # Reduced gravity force
        point.update(dt)

    for _ in range(5):  # Increased number of constraint iterations for more stiffness
        for i in range(len(rope) - 1):
            rope[i].constrain(rope[i + 1], segment_length)
        # Constrain the first and last points to fixed positions
        rope[0].pos = pygame.math.Vector2(start_pos) + parallax_offset
        rope[-1].pos = pygame.math.Vector2(end_pos)

def draw_rope(screen, rope):
    for i in range(len(rope) - 1):
        pygame.draw.line(screen, CONNECTION_COLOR, rope[i].pos, rope[i + 1].pos, 2)