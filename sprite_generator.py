# sprite_generator.py

import pygame
import numpy as np
from scipy.ndimage import gaussian_filter
import os

pygame.init()

def create_particle_sprites(base_size=64, num_levels=20):
    sprites = []
    
    # Create base particle (a white circle)
    base_surface = pygame.Surface((base_size, base_size), pygame.SRCALPHA)
    pygame.draw.circle(base_surface, (125, 125, 125, 255), (base_size // 2, base_size // 2), base_size // 8)
    
    # Convert surface to numpy array
    base_array = pygame.surfarray.array3d(base_surface)
    alpha = pygame.surfarray.array_alpha(base_surface)
    
    for i in range(num_levels):
        # Calculate blur sigma based on level
        sigma = i * 0.7
        
        # Apply Gaussian blur
        blurred_array = gaussian_filter(base_array, sigma=(sigma, sigma, 0))
        blurred_alpha = gaussian_filter(alpha, sigma=sigma)
        
        # Create new surface
        blurred_surface = pygame.Surface((base_size, base_size), pygame.SRCALPHA)
        
        # Convert blurred arrays back to uint8
        blurred_array = np.clip(blurred_array, 0, 255).astype(np.uint8)
        blurred_alpha = np.clip(blurred_alpha, 0, 255).astype(np.uint8)
        
        # Update surface pixels
        pygame.surfarray.blit_array(blurred_surface, blurred_array)
        pygame.surfarray.pixels_alpha(blurred_surface)[:] = blurred_alpha
        
        sprites.append(blurred_surface)
        
        # Save sprite as an image file for inspection
        pygame.image.save(blurred_surface, f"images/particle_sprite_{i}.png")
    
    return sprites

# Generate sprites
particle_sprites = create_particle_sprites(base_size=64, num_levels=20)

print(f"Generated {len(particle_sprites)} particle sprites.")
print("Sprite images saved in the current directory for inspection.")