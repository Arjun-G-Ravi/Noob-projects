import pygame
from platforms import platforms
import os
import sys

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Function to get the correct path for assets
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)

# Constants
WIDTH, HEIGHT = 500, 700
GRAVITY = 0.5
JUMP_STRENGTH = -11.5
PLAYER_SPEED = 5
MAX_POSSIBLE_HEIGHT = 100
WALL_BOUNCE = -5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rohit Jump")

# Load player sprite and sound with resource_path
player_img = pygame.image.load(resource_path("player2.png")).convert_alpha()
player_img = pygame.transform.scale(player_img, (70, 70))
player = pygame.Rect(WIDTH // 4, HEIGHT - 100, 70, 70)
velocity_y = 0
velocity_x = 0
on_ground = False
current_height = 0
max_height = 0
best_height = 0
last_height = 0
fall_sound = pygame.mixer.Sound(resource_path("fall.ogg"))
sound_played = False
falling = False
last_platform_height = 0

# Load win sprite with resource_path
win_img = pygame.image.load(resource_path("win.png")).convert_alpha()
win_img = pygame.transform.scale(win_img, (50, 50))

# Font and clock
font = pygame.font.SysFont(None, 30)
clock = pygame.time.Clock()
running = True
win = False

while running:
    screen.fill(WHITE)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        velocity_x = -PLAYER_SPEED
    elif keys[pygame.K_RIGHT]:
        velocity_x = PLAYER_SPEED
    else:
        velocity_x = 0
    if keys[pygame.K_SPACE] and on_ground:
        velocity_y = JUMP_STRENGTH
    if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
        running = False

    # Apply gravity and movement
    velocity_y += GRAVITY
    player.y += velocity_y
    player.x += velocity_x
    on_ground = False

    # Collision with platforms and height update
    for platform in platforms:
        if player.colliderect(platform['rect']) and velocity_y > 0:
            player.y = platform['rect'].y - player.height
            velocity_y = 0
            on_ground = True
            current_height = platform['height_level']
            max_height = max(max_height, current_height)
            best_height = max(best_height, current_height)
            sound_played = False
            break

    # Wall collision
    if player.x < 0:
        player.x = 0
    if player.x > WIDTH - player.width:
        player.x = WIDTH - player.width

    # Vertical scrolling
    if player.y < HEIGHT // 2 and velocity_y < 0:
        shift = HEIGHT // 2 - player.y
        player.y = HEIGHT // 2
        for platform in platforms:
            platform['rect'].y += shift
    elif player.y > HEIGHT // 2 and velocity_y > 0:
        shift = player.y - HEIGHT // 2
        player.y = HEIGHT // 2
        for platform in platforms:
            platform['rect'].y -= shift

    # Fall detection using height difference
    if velocity_y > 0 and not on_ground:
        if not falling:
            falling = True
    elif on_ground and falling:
        fall_distance = last_platform_height - current_height
        last_platform_height = current_height
        if fall_distance > 2 and not sound_played:
            fall_sound.play()
            sound_played = True
        falling = False

    # Reset if fallen to bottom (height 0)
    if current_height == 0 and last_height > 0 and falling:
        player.x = WIDTH // 2
        player.y = HEIGHT - 100
        velocity_y = 0
        velocity_x = 0
        max_height = 0
        falling = False

    # Draw player, win sprite, and platforms
    screen.blit(player_img, (player.x, player.y))
    # Find the highest platform
    highest_platform = max(platforms, key=lambda p: p['height_level'])
    highest_rect = highest_platform['rect']
    highest_height = highest_platform['height_level']
    # Place win sprite one block above the highest platform
    win_rect = win_img.get_rect(center=(highest_rect.centerx, highest_rect.centery - 20))
    screen.blit(win_img, win_rect)
    # Draw all platforms
    for platform in platforms:
        pygame.draw.rect(screen, BLACK, platform['rect'])
    # Check if player touches the win sprite
    if player.colliderect(win_rect):
        running = False
        win = True

    # Display height tracker
    height_text = font.render(f"Height: {current_height}m | Max: {max_height}m | Best: {best_height}m", True, BLACK)
    screen.blit(height_text, (10, 10))

    # Update last height
    last_height = current_height

    pygame.display.flip()
    clock.tick(60)

# Display a "You Win!" message before quitting if won
screen.fill(WHITE)
if win:
    win_image = pygame.image.load(resource_path('win.jpeg'))  # Use resource_path here too
    win_image = pygame.transform.scale(win_image, (WIDTH, HEIGHT))
    win_rect = win_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(win_image, win_rect)
    
    # Add "You Win!" text overlay
    font = pygame.font.SysFont(None, 100)
    win_text = font.render("You Win!", True, (255, 255, 255))
    outline_text = font.render("You Win!", True, (0, 0, 0))
    text_rect = win_text.get_rect(topleft=(10, 30))
    
    screen.blit(outline_text, (text_rect.x + 2, text_rect.y + 2))
    screen.blit(win_text, text_rect)
    
    pygame.display.flip()
    pygame.time.wait(5000)
pygame.quit()