import pygame

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 500, 700
GRAVITY = 0.5
JUMP_STRENGTH = -10
PLAYER_SPEED = 5
PLATFORM_WIDTH, PLATFORM_HEIGHT = 100, 10
MAX_HEIGHT_METERS = 100  # Maximum height in meters
METERS_PER_JUMP = 1  # Each platform is 1 meter higher
PIXELS_PER_METER = 10  # 10 pixels per meter

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jump King Clone")

# Player setup
player = pygame.Rect(WIDTH // 2, HEIGHT - 100, 30, 30)
velocity_y = 0
on_ground = False
current_height = 0
max_height = 0

# Generate platforms
platforms = [pygame.Rect(200, HEIGHT - 200, PLATFORM_WIDTH, PLATFORM_HEIGHT)]
for i in range(1, MAX_HEIGHT_METERS + 1):
    y_position = HEIGHT - 200 - (i * PIXELS_PER_METER)
    x_position = (i * 123) % WIDTH  # Spread platforms horizontally
    platforms.append(pygame.Rect(x_position, y_position, PLATFORM_WIDTH, PLATFORM_HEIGHT))

font = pygame.font.SysFont(None, 30)
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        player.x += PLAYER_SPEED
    if keys[pygame.K_SPACE] and on_ground:
        velocity_y = JUMP_STRENGTH
    
    # Apply gravity
    velocity_y += GRAVITY
    player.y += velocity_y
    on_ground = False
    
    # Collision with platforms
    for platform in platforms:
        if player.colliderect(platform) and velocity_y > 0:
            player.y = platform.y - player.height
            velocity_y = 0
            on_ground = True
            current_height = (HEIGHT - platform.y) // PIXELS_PER_METER  # Update current height
            max_height = max(max_height, current_height)  # Track highest point reached
            break

    # Vertical scrolling
    if player.y < HEIGHT // 2 and velocity_y < 0:
        shift = HEIGHT // 2 - player.y
        player.y = HEIGHT // 2
        for platform in platforms:
            platform.y += shift
    elif player.y > HEIGHT // 2 and velocity_y > 0:
        shift = player.y - HEIGHT // 2
        player.y = HEIGHT // 2
        for platform in platforms:
            platform.y -= shift
    
    # Reset if player falls too far
    if player.y - velocity_y > HEIGHT:
        player.x = WIDTH // 2
        player.y = HEIGHT - 100
        velocity_y = 0
        current_height = 0  # Reset height on fall

    # Keep player within horizontal bounds
    if player.x < 0:
        player.x = 0
    if player.x > WIDTH - player.width:
        player.x = WIDTH - player.width

    # Draw player and platforms
    pygame.draw.rect(screen, RED, player)
    for platform in platforms:
        pygame.draw.rect(screen, BLACK, platform)
    
    # Display height tracker
    height_text = font.render(f"Height: {current_height}m | Max: {max_height}m", True, BLACK)
    screen.blit(height_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
