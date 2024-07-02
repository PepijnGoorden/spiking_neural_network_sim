import pygame
import math
from settings import *

# Neuron list
neurons = []

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
        self.state_active = False
        self.resting_voltage = 0  # Initial resting_voltage
        self.resting_time_constant = R1 * C1  # Time constant
        self.external_stimulation = 0
        self.weight = 0.25
        self.trainig_factor = 0.01

    def draw(self, screen, current_mouse_offset):
        color = SPIKE_COLOR if self.state_active else NEURON_COLOR #Change SPIKE_COLOR in dark mode
        # Calculate parallax offset assuming neurons are always at the focus depth
        parallax_offset = current_mouse_offset * (1 - (FOCUS_DEPTH / MAX_DEPTH)) * PARALAX_SCALE
        screen_pos = (int(self.x + parallax_offset.x), int(self.y + parallax_offset.y))
        pygame.draw.circle(screen, color, screen_pos, NEURON_RADIUS + self.resting_voltage)

        # Draw the resting voltage text
        font = pygame.font.Font(None, 24)  # You may need to adjust the font size
        text = font.render(f"{self.resting_voltage:.2f}", True, (0, 0, 0))
        text_pos = (screen_pos[0] - (NEURON_RADIUS * 1.5), screen_pos[1] + NEURON_RADIUS + 5)  # Position under the neuron
        screen.blit(text, text_pos)
        text = font.render(f"{self.weight:.2f}", True, (0, 0, 0))
        text_pos = (screen_pos[0] - (NEURON_RADIUS * 1.5), screen_pos[1] + NEURON_RADIUS + 20)  # Position under the neuron
        screen.blit(text, text_pos)
            
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

    def fire(self):
        self.state_active = True
        for connection in self.connections_to:
            connection.is_animating = True
            connection.animation_progress = 0  # Reset animation progress when firing
            self.resting_voltage = 0  # Reset resting voltage after firing

    def update_neuron(self, dt):
        if self.state_active:
            all_animations_finished = True
            for connection in self.connections_to:
                if connection.is_animating:
                    connection.animation_progress += dt * SIGNAL_PROPAGATION_FACTOR
                    if connection.animation_progress >= connection.segments:
                        connection.is_animating = False
                        self.weight += self.trainig_factor
                        connection.connected_to.external_stimulation += 25 * self.weight
                    else:
                        all_animations_finished = False
            
            if all_animations_finished:
                self.state_active = False

        else:
            # Apply external stimulation immediately
            if self.external_stimulation > 0:
                self.resting_voltage += (V_MAX - self.resting_voltage) * (self.external_stimulation * dt / self.resting_time_constant)
            
            # Decay resting voltage and weight
            self.resting_voltage *= math.exp(-dt / self.resting_time_constant)
            if self.weight > 0.1:
                self.weight -= self.trainig_factor / 100
            
            # Check if threshold is reached
            if self.resting_voltage >= V_THRESHOLD:
                self.fire()
        
        # Reset external stimulation at the end of each update
        self.external_stimulation = 0

    def draw_connections(self, screen, current_mouse_offset):
        parallax_offset = current_mouse_offset * (1 - (FOCUS_DEPTH / MAX_DEPTH)) * PARALAX_SCALE
        for connection in self.connections_to:
            from_pos = pygame.math.Vector2(
                int(connection.connected_from.x + parallax_offset.x),
                int(connection.connected_from.y + parallax_offset.y)
            )
            to_pos = pygame.math.Vector2(
                int(connection.connected_to.x + parallax_offset.x),
                int(connection.connected_to.y + parallax_offset.y)
            )

            segment_vector = (to_pos - from_pos) / connection.segments
            
            for i in range(connection.segments):
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

                pygame.draw.line(screen, color, start, end, width)

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