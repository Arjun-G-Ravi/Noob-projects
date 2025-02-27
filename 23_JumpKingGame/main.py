import pygame

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 500, 700
GRAVITY = 0.5
JUMP_STRENGTH = -10
PLAYER_SPEED = 5
PLATFORM_WIDTH, PLATFORM_HEIGHT = 100, 10

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


platforms = [  # (x, y, width, height)
    pygame.Rect(0, 400, 800, 500),
    pygame.Rect(200, 300, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(300, 200, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(100, 100, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(100, 0, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(250, -100, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(150, -200, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(350, -300, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(350, -400, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(350, -500, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(200, -600, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(300, -700, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(100, -800, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(250, -900, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(150, -1000, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(350, -1100, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(200, -1200, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(300, -1300, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(100, -1400, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(250, -1500, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(150, -1600, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(350, -1700, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(200, -1800, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(300, -1900, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(100, -2000, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(250, -2100, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(150, -2200, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(350, -2300, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(200, -2400, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(300, -2500, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(100, -2600, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(250, -2700, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(150, -2800, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(350, -2900, PLATFORM_WIDTH, PLATFORM_HEIGHT),
    pygame.Rect(200, -3000, PLATFORM_WIDTH, PLATFORM_HEIGHT),
]


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
            break

    # Vertical scrolling:
    # If the player goes above the midline (jumping), scroll platforms down.
    if player.y < HEIGHT // 2 and velocity_y < 0:
        shift = HEIGHT // 2 - player.y
        player.y = HEIGHT // 2
        for platform in platforms:
            platform.y += shift
    # If the player goes below the midline (falling), scroll platforms up.
    elif player.y > HEIGHT // 2 and velocity_y > 0:
        shift = player.y - HEIGHT // 2
        player.y = HEIGHT // 2
        for platform in platforms:
            platform.y -= shift

    # Optional: Reset if the player falls too far (e.g., if platforms have scrolled out)
    if player.y - velocity_y > HEIGHT:
        player.x = WIDTH // 2
        player.y = HEIGHT - 100
        velocity_y = 0

    # Keep player within horizontal bounds
    if player.x < 0:
        player.x = 0
    if player.x > WIDTH - player.width:
        player.x = WIDTH - player.width

    # Draw player and platforms
    pygame.draw.rect(screen, RED, player)
    for platform in platforms:
        pygame.draw.rect(screen, BLACK, platform)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
