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
    {'rect': pygame.Rect(250, -700, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 11},
    {'rect': pygame.Rect(300, -800, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 12},
    {'rect': pygame.Rect(150, -900, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 13},
    {'rect': pygame.Rect(200, -1000, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 14},
    {'rect': pygame.Rect(250, -1100, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 15},
    {'rect': pygame.Rect(100, -1200, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 16},
    {'rect': pygame.Rect(350, -1300, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 17},
    {'rect': pygame.Rect(300, -1400, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 18},
    {'rect': pygame.Rect(150, -1500, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 19},
    {'rect': pygame.Rect(200, -1600, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 20},
    {'rect': pygame.Rect(250, -1700, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 21},
    {'rect': pygame.Rect(350, -1800, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 22},
    {'rect': pygame.Rect(100, -1900, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 23},
    {'rect': pygame.Rect(200, -2000, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 24},
    {'rect': pygame.Rect(300, -2100, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 25},
    {'rect': pygame.Rect(150, -2200, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 26},
    {'rect': pygame.Rect(350, -2300, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 27},
    {'rect': pygame.Rect(100, -2400, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 28},
    {'rect': pygame.Rect(200, -2500, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 29},
    {'rect': pygame.Rect(250, -2600, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 30},
    {'rect': pygame.Rect(300, -2700, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 31},
    {'rect': pygame.Rect(350, -2800, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 32},
    {'rect': pygame.Rect(150, -2900, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 33},
    {'rect': pygame.Rect(100, -3000, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 34},
    {'rect': pygame.Rect(250, -3100, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 35},
    {'rect': pygame.Rect(200, -3200, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 36},
    {'rect': pygame.Rect(300, -3300, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 37},
    {'rect': pygame.Rect(350, -3400, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 38},
    {'rect': pygame.Rect(150, -3500, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 39},
    {'rect': pygame.Rect(100, -3600, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 40},
    {'rect': pygame.Rect(250, -3700, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 41},
    {'rect': pygame.Rect(300, -3800, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 42},
    {'rect': pygame.Rect(200, -3900, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 43},
    {'rect': pygame.Rect(350, -4000, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 44},
    {'rect': pygame.Rect(150, -4100, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 45},
    {'rect': pygame.Rect(100, -4200, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 46},
    {'rect': pygame.Rect(250, -4300, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 47},
    {'rect': pygame.Rect(300, -4400, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 48},
    {'rect': pygame.Rect(200, -4500, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 49},
    {'rect': pygame.Rect(350, -4600, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 50},
    {'rect': pygame.Rect(100, -4700, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 51},
    {'rect': pygame.Rect(200, -4800, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 52},
    {'rect': pygame.Rect(250, -4900, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 53},
    {'rect': pygame.Rect(150, -5000, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 54},
    {'rect': pygame.Rect(350, -5100, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 55},
    {'rect': pygame.Rect(100, -5200, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 56},
    {'rect': pygame.Rect(200, -5300, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 57},
    {'rect': pygame.Rect(300, -5400, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 58},
    {'rect': pygame.Rect(250, -5500, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 59},
    {'rect': pygame.Rect(350, -5600, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 60},
    {'rect': pygame.Rect(150, -5700, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 61},
    {'rect': pygame.Rect(100, -5800, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 62},
    {'rect': pygame.Rect(250, -5900, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 63},
    {'rect': pygame.Rect(300, -6000, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 64},
    {'rect': pygame.Rect(200, -6100, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 65},
    {'rect': pygame.Rect(350, -6200, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 66},
    {'rect': pygame.Rect(100, -6300, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 67},
    {'rect': pygame.Rect(150, -6400, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 68},
    {'rect': pygame.Rect(250, -6500, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 69},
    {'rect': pygame.Rect(300, -6600, PLATFORM_WIDTH, PLATFORM_HEIGHT), 'height_level': 70},
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