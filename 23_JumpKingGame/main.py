import pygame

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 500, 700
GRAVITY = 0.5
JUMP_STRENGTH = -10
PLAYER_SPEED = 5
PLATFORM_WIDTH, PLATFORM_HEIGHT = 100, 10
MAX_POSSIBLE_HEIGHT = 10  # Maximum height set to 10 meters

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
current_height = 0  # Initial height set to 0
max_height = 0      # Maximum height in current attempt
best_height = 0     # Track player's best height across all attempts

# Platforms with fixed height levels (0 to 10 meters)
platforms = [
    {'rect': pygame.Rect(0, 400, 800, 500), 'height_level': 0},   # Ground
    {'rect': pygame.Rect(200, 300, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 1},
    {'rect': pygame.Rect(300, 200, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 2},
    {'rect': pygame.Rect(100, 100, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 3},
    {'rect': pygame.Rect(100, 0, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 4},
    {'rect': pygame.Rect(250, -100, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 5},
    {'rect': pygame.Rect(150, -200, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 6},
    {'rect': pygame.Rect(350, -300, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 7},
    {'rect': pygame.Rect(350, -400, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 8},
    {'rect': pygame.Rect(350, -500, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 9},
    {'rect': pygame.Rect(200, -600, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 10},
]

# Font and clock
font = pygame.font.SysFont(None, 30)
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
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

    # Collision with platforms and height update
    for platform in platforms:
        if player.colliderect(platform['rect']) and velocity_y > 0:
            player.y = platform['rect'].y - player.height
            velocity_y = 0
            on_ground = True
            current_height = platform['height_level'] 
            max_height = 100
            best_height = max(best_height, current_height) 
            break

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

    # Reset if player falls too far
    if player.y - velocity_y > HEIGHT:
        player.x = WIDTH // 2
        player.y = HEIGHT - 100
        velocity_y = 0
        current_height = 0   # Reset current height
        max_height = 0       # Reset max height for new attempt

    # Keep player within horizontal bounds
    if player.x < 0:
        player.x = 0
    if player.x > WIDTH - player.width:
        player.x = WIDTH - player.width

    # Draw player and platforms
    pygame.draw.rect(screen, RED, player)
    for platform in platforms:
        pygame.draw.rect(screen, BLACK, platform['rect'])

    # Display height tracker
    height_text = font.render(f"Height: {current_height}m | Max: {max_height}m | Best: {best_height}m", True, BLACK)
    screen.blit(height_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()