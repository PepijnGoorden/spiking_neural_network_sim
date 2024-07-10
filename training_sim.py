import pygame
from settings import *

is_thrusting = False

class TrainingSim:
    def __init__(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height

        # Rocket properties
        self.rocket_width = 5
        self.rocket_height = 15
        self.rocket_x = self.WIDTH // 2 - self.rocket_width // 2
        self.rocket_y = self.HEIGHT // 2
        self.velocity = 0
        self.position_data = self.rocket_y
        self.gravity = 0.05
        self.thrust = -0.3

        # Velocity limits
        self.MIN_VEL = self.thrust * 10
        self.MAX_VEL = self.thrust * -10

        # Font setup
        self.font = pygame.font.Font(None, 16)

    def update(self, is_thrusting):
        # Apply gravity
        self.velocity += self.gravity
        
        # Apply thrust if up arrow is pressed
        if is_thrusting:
            self.velocity += self.thrust
        
        # Limit velocity
        self.velocity = max(self.MIN_VEL, min(self.velocity, self.MAX_VEL))
        
        # Update rocket position
        self.rocket_y += self.velocity
        
        # Keep rocket within screen bounds
        self.rocket_y = max(0, min(self.rocket_y, self.HEIGHT - self.rocket_height))
        
        # Calculate position_data
        self.position_data = int((self.rocket_y + self.rocket_height / 2 - self.HEIGHT / 2) / (self.HEIGHT / 2) * 100)

    def draw(self, surface):
        # Clear the surface
        surface.fill(WHITE)
        
        # Draw the rocket
        pygame.draw.rect(surface, BLACK, (self.rocket_x, self.rocket_y, self.rocket_width, self.rocket_height))
        
        # Draw the center line
        pygame.draw.line(surface, BLACK, (0, self.HEIGHT // 2), (self.WIDTH, self.HEIGHT // 2))
        
        # Draw the position_data
        position_data_text = self.font.render(f"Position: {self.position_data * -1}", True, BLACK)
        surface.blit(position_data_text, (10, 10))
        
        # Draw the velocity
        vel_text = self.font.render(f"Velocity: {self.velocity * -1:.2f}", True, BLACK)
        surface.blit(vel_text, (10, 26))

def create_training_sim(width, height):
    return TrainingSim(width, height)

def convert_game_output_to_neuron_input(position, velocity):
    # Convert position to "too low" and "too high" inputs
    position_too_low = max(position / 100, 0)  # 0 when position >= 0, 1 when position = -100
    position_too_high = max(-position / 100, 0)  # 0 when position <= 0, 1 when position = 100
    
    # Normalize position and velocity to a range between 0 and 1
    normalized_velocity = (velocity + 3) / 6      # -3 to 3 -> 0 to 1

    # Convert normalized values to membrane potential increases
    position_low_input = position_too_low * ACTION_POTENTIAL
    position_high_input = position_too_high * ACTION_POTENTIAL
    velocity_input = normalized_velocity * ACTION_POTENTIAL

    return position_low_input, position_high_input, velocity_input

def stimulate_neuron_with_game_output(position, velocity):
    position_low_input, position_high_input, velocity_input = convert_game_output_to_neuron_input(position, velocity)
    return position_low_input, position_high_input, velocity_input