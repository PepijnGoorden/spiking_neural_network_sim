import pygame
import math
from settings import *
import os
from enum import Enum, auto

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
        self.receiving_neuron = target_neuron
        self.segments = CONNECTION_SEGMENTS
        self.propagation_progress = 0
        self.is_propagating = False
        self.weight = 0.25 # Start weight

class NeuronType(Enum):
    REGULAR = auto()
    POSITION_INPUT = auto()
    VELOCITY_INPUT = auto()
    OUTPUT = auto()

class Neuron:
    def __init__(self, x, y, neuron_type):
        self.x = x
        self.y = y
        self.connections_to = []  # Connections to other neurons
        self.connections_from = []  # Neurons that connect to this neuron
        self.is_firing = False # Is the neuron in the active state?
        self.membrane_potential = 0  # Stimulation level / membrane potential
        self.neuron_type = neuron_type

    #NEURON BEHAVIOR
    def fire(self):
        self.is_firing = True # Set is_firing flag
        self.membrane_potential = 0  # Reset stimulation level (membrane_potential) after firing

        # Start propagation of action_potential through all connections
        for connection in self.connections_to:
            connection.is_propagating = True
            connection.propagation_progress = 0  # Reset propagation progress when firing
    
    def propagate_action_potentials(self, dt):
        # Find all connections that are currently propagating and store them in propagating_connections[]
        propagating_connections = [connection for connection in self.connections_to if connection.is_propagating]
        
        # Update each propagating connection
        for connection in propagating_connections[:]: # "[:]" = "slice copy", a copy for safe modification while using it in the loop
            # Increment propagation_progress 
            connection.propagation_progress += dt * AXON_SPEED_FACTOR
            
            # Check if end of connection segments is reached -> Action potential reached the destination neuron
            if connection.propagation_progress >= connection.segments:
                # Stop propagation
                connection.is_propagating = False
                propagating_connections.remove(connection)

                # Increase connection weight
                connection.weight += TRAINING_INCREMENT

                # Stimulate receiving neuron, if it is not firing
                if not connection.receiving_neuron.is_firing:
                    self.stimulate_receiving_neuron(connection)
        
        # Check if there are no more remaining active connections
        if len(propagating_connections) <= 0:
            self.is_firing = False

    def stimulate_receiving_neuron(self, connection):
        # Modify action potential with connection weight
        postsynaptic_action_potential = ACTION_POTENTIAL * connection.weight

        # Stimulate receiving neuron: Increase the membrane potentials of the neuron this 'connection' is connected to (post synaptic neuron)
        connection.receiving_neuron.membrane_potential += postsynaptic_action_potential

    # DRAW and UPDATE events
    def update_neuron(self, dt):
        # ACTIVE STATE
        if self.is_firing:
            self.propagate_action_potentials(dt)                        

        # RESTING STATE
        else:
            # # Apply external stimulation
            # if self.membrane_potential > 0:
            #     self.membrane_potential += (V_MAX - self.membrane_potential) * (self.membrane_potential * dt / self.resting_time_constant)
            
            # Decay membrane_potential
            self.membrane_potential *= math.exp(-dt / TAU)

            for connection in self.connections_to:
                # if connection weight will not go below 0
                if not connection.weight - (TRAINING_INCREMENT / 100) <= 0:
                    # reduce the connection weight
                    connection.weight -= TRAINING_INCREMENT / 100
            
            # Check if threshold is reached
            if self.membrane_potential >= V_THRESHOLD:
                self.fire()

    def draw_neuron(self, screen, current_mouse_offset, neuron_info):
        # Calculate parallax offset assuming neurons are always at the focus depth
        parallax_offset = current_mouse_offset * (1 - (FOCUS_DEPTH / MAX_DEPTH)) * PARALAX_SCALE
        screen_pos = (int(self.x + parallax_offset.x), int(self.y + parallax_offset.y))

        # Draw the components
        self.draw_connections(screen, parallax_offset)
        self.draw_self(screen, screen_pos)
        self.draw_info(screen, parallax_offset, screen_pos, neuron_info)

    def draw_self(self, screen, screen_pos):
        # Draw the neuron
        if self.neuron_type == NeuronType.REGULAR:
            pygame.draw.circle(screen, NEURON_COLOR, screen_pos, NEURON_RADIUS)
            # Draw neuron firing state
            if self.is_firing:
                pygame.draw.circle(screen, SPIKE_COLOR, screen_pos, NEURON_RADIUS / 2)
        elif self.neuron_type == NeuronType.POSITION_INPUT:
            pygame.draw.circle(screen, WHITE, screen_pos, NEURON_RADIUS)
            pygame.draw.circle(screen, NEURON_COLOR, screen_pos, NEURON_RADIUS, width=4)
            # Draw neuron firing state
            if self.is_firing:
                pygame.draw.circle(screen, NEURON_COLOR, screen_pos, NEURON_RADIUS / 2)
        elif self.neuron_type == NeuronType.VELOCITY_INPUT:
            pygame.draw.circle(screen, WHITE, screen_pos, NEURON_RADIUS)
            pygame.draw.circle(screen, NEURON_COLOR, screen_pos, NEURON_RADIUS, width=2)
            # Draw neuron firing state
            if self.is_firing:
                pygame.draw.circle(screen, NEURON_COLOR, screen_pos, NEURON_RADIUS / 2)
        else:
            pygame.draw.circle(screen, WHITE, screen_pos, NEURON_RADIUS)
            pygame.draw.circle(screen, NEURON_COLOR, screen_pos, NEURON_RADIUS / 2)
            pygame.draw.circle(screen, NEURON_COLOR, screen_pos, NEURON_RADIUS, width=2)
            # Draw neuron firing state
            if self.is_firing:
                pygame.draw.circle(screen, SPIKE_COLOR, screen_pos, NEURON_RADIUS / 2)

    def draw_info(self, screen, parallax_offset, screen_pos, neuron_info):
        # Draw membrane_potential info
        if neuron_info:
            font = pygame.font.Font(None, 24)  # You may need to adjust the font size
            text = font.render(f"{self.membrane_potential:.2f}", True, (0, 0, 0))
            text_pos = (screen_pos[0] - (NEURON_RADIUS * 1.5), screen_pos[1] + NEURON_RADIUS + 5)  # Position under the neuron
            screen.blit(text, text_pos)

        # Draw connection weight info halfway the connection
        for connection in self.connections_to:
            if neuron_info:
                position = (
                    (connection.receiving_neuron.x + connection.connected_from.x) / 2 + parallax_offset[0], 
                    (connection.receiving_neuron.y + connection.connected_from.y) / 2 + parallax_offset[1]
                )
                font = pygame.font.Font(None, 24)  # You may need to adjust the font size
                text = font.render(f"{connection.weight:.2f}", True, (0, 0, 0))
                text_pos = (position[0], position[1])  # Position under the connection
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
                int(connection.receiving_neuron.x + parallax_offset.x),
                int(connection.receiving_neuron.y + parallax_offset.y)
            )

            # Determine the segment length by getting the distance between to and from and deviding them by the number of segments
            segment_vector = (to_pos - from_pos) / connection.segments
            
            # Loop through all segments
            for i in range(connection.segments):
                # Determen where the segment starts and ends
                start = from_pos + segment_vector * i
                end = from_pos + segment_vector * (i + 1)
                
                # Determine line width based on animation state
                if connection.is_propagating:
                    progress = connection.propagation_progress - i
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
        if not any(connection.receiving_neuron == target_neuron for connection in self.connections_to):
            new_connection = Connection(self, target_neuron)
            self.connections_to.append(new_connection)
            target_neuron.connections_from.append(self)

    def remove_connection(self, target_neuron):
        self.connections_to = [connection for connection in self.connections_to if connection.receiving_neuron != target_neuron]
        target_neuron.connections_from.remove(self)

    def remove_all_connections(self):
        for connection in self.connections_to[:]:
            self.remove_connection(connection.receiving_neuron)
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