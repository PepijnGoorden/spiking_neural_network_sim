import pygame
import math
from random import uniform, randint
from settings import *
from utilities import *
# from sprite_generator import particle_sprites
import os

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

particle_group = pygame.sprite.Group()
PARTICLE_TIMER_EVENT = pygame.event.custom_type()

# Load particle sprites
bg_particle_sprites = []
bg_sprite_dir = "resources/img/bg_particles"
for i in range(20):  # Adjust this range based on your number of sprites
    bg_sprite_path = os.path.join(bg_sprite_dir, f"particle_{i}.png")
    sprite = pygame.image.load(bg_sprite_path).convert_alpha()
    bg_particle_sprites.append(sprite)

def setup_particle_timer():
    pygame.time.set_timer(PARTICLE_TIMER_EVENT, PARTICLE_SPAWN_INTERVAL)
    return PARTICLE_TIMER_EVENT

def spawn_background_particle(fading_in):
    if len(particle_group) < MAX_PARTICLE_COUNT:
        pos = [
            uniform(0, WINDOW_WIDTH),
            uniform(0, WINDOW_HEIGHT)
        ]
        depth = uniform(MIN_DEPTH, MAX_DEPTH)
        direction = pygame.math.Vector2(uniform(-1, 1), uniform(-1, 1))
        speed = randint(1, 50)
        fade_speed = uniform(10, 150)
        Particle(particle_group, pos, depth, direction, speed, fade_speed, fading_in)

class Particle(pygame.sprite.Sprite):
    def __init__(self, groups, pos, depth, direction, speed, fade_speed, fading_in):
        super().__init__(groups)
        self.pos = pygame.math.Vector2(pos)
        self.depth = depth
        self.direction = direction
        self.speed = speed
        self.fading_in = fading_in

        if depth == FOCUS_DEPTH:
            self.sprite_index =  0  # Sharpest image at the focus point
        elif depth == MIN_DEPTH or depth == MAX_DEPTH:
            self.sprite_index = len(bg_particle_sprites) - 1  # Blurred images at the extremes
        elif depth < FOCUS_DEPTH:
            normalized_depth = (FOCUS_DEPTH - depth) / FOCUS_DEPTH
            sprite_index = int(normalized_depth * (len(bg_particle_sprites) - 1))
        else:
            normalized_depth = (depth - FOCUS_DEPTH) / (MAX_DEPTH - FOCUS_DEPTH)
            sprite_index = int(normalized_depth * (len(bg_particle_sprites) - 1))
        
        self.sprite_index = max(0, min(sprite_index, len(bg_particle_sprites) - 1))  # Ensure index is within bounds
        
        # Size calculation
        self.size_factor = 1 - ((self.depth - MIN_DEPTH) / (MAX_DEPTH - MIN_DEPTH))
        self.size_factor = max(0.1, min(self.size_factor, 1))  # Clamp between 0.1 and 1
        
        # Get the original sprite and scale it
        original_sprite = bg_particle_sprites[self.sprite_index]
        original_size = original_sprite.get_width()  # Assuming square sprites
        new_size = int(original_size * self.size_factor)
        
        if new_size != original_size:
            self.original_image = pygame.transform.smoothscale(original_sprite, (new_size, new_size))
        else:
            self.original_image = original_sprite

        # Alpha calculation
        self.base_alpha = int(255 * (1 - ((self.depth - MIN_DEPTH) / (MAX_DEPTH - MIN_DEPTH))))
        self.base_alpha = max(30, min(self.base_alpha, 255))  # Ensure minimum visibility

        self.image = self.original_image.copy()
        self.image.set_alpha(self.base_alpha)
        self.rect = self.image.get_rect(center=self.pos)

        if fading_in:
            self.current_alpha = 1
        else:
            self.current_alpha = self.base_alpha
        self.image.set_alpha(self.current_alpha)
        self.fade_speed = fade_speed

    def move(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

    def fade(self, dt):
            if self.fading_in:
                self.current_alpha += self.fade_speed * dt
                if self.current_alpha >= self.base_alpha:
                    self.current_alpha = self.base_alpha
                    self.fading_in = False
            else:
                self.current_alpha -= self.fade_speed * dt
            
            self.current_alpha = max(0, min(self.current_alpha, self.base_alpha))
            self.image.set_alpha(int(self.current_alpha))

            if self.current_alpha <= 0:
                self.kill()

    def update(self, dt):
        self.move(dt)
        self.fade(dt)

def update_and_draw_particles(screen, dt):
    for particle in particle_group:
        particle.update(dt)
        
        # Normalize depth
        normalized_depth = (particle.depth - MIN_DEPTH) / (MAX_DEPTH - MIN_DEPTH)
        
        # Calculate parallax offset based on normalized depth
        if particle.depth == MAX_DEPTH:
            parallax_offset = pygame.math.Vector2(0, 0)
        else:
            parallax_speed = (2 / 3) * (1 - normalized_depth)
            parallax_offset = current_mouse_offset * parallax_speed * PARALAX_SCALE
        
        draw_pos = particle.pos + parallax_offset
        
        # Directly blit the particle image
        screen.blit(particle.image, draw_pos)

# Drawing utilities
def create_vignette_surface(width, height, outer_alpha=128, center_radius=0.5, color=(0, 0, 0)):
    vignette_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    center_x, center_y = width // 2, height // 2
    max_distance = math.sqrt(center_x**2 + center_y**2) * center_radius

    for y in range(height):
        for x in range(width):
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            if distance < max_distance:
                alpha = 0
            else:
                alpha = int(((distance - max_distance) / (max_distance * (1 / center_radius))) * outer_alpha)
                alpha = min(alpha, outer_alpha)
            vignette_surface.set_at((x, y), color + (alpha,))
    
    return vignette_surface

# Create vignette surface
vignette = create_vignette_surface(WINDOW_WIDTH, WINDOW_HEIGHT, 100, 0.3)