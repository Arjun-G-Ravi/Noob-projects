import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Shooter")

# Game constants
FOV = 60 * (math.pi / 180)
NUM_RAYS = WIDTH
MOVE_SPEED = 0.2
MOUSE_SENSITIVITY = 0.002

# Enemy
BOSS_SPEED = 0.01
REGULAR_SPEED = 0.05
FAST_SPEED = 0.1


# Define the larger maze (20x20)
MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Fonts
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)

# Game states
MAIN_MENU, PLAYING, GAME_OVER = 0, 1, 2
game_state = MAIN_MENU

# Player variables
def reset_player():
    global player_x, player_y, player_angle, player_health, player_ammo, enemies, powerups
    player_x = 1.5
    player_y = 1.5
    player_angle = 0
    player_health = 100
    player_ammo = 100
    enemies = [
        {"x": 5.5, "y": 3.5, "type": "regular", "health": 10, "max_health": 10},
        {"x": 7.5, "y": 5.5, "type": "regular", "health": 10, "max_health": 10},
        {"x": 18.5, "y": 18.5, "type": "boss", "health": 70, "max_health": 70, "last_spawn_time": 0}
    ]
    powerups = [
        {"x": 5.5, "y": 5.5, "type": "health"},
        {"x": 12.5, "y": 12.5, "type": "health"},
        {"x": 3.5, "y": 16.5, "type": "ammo"},
        {"x": 16.5, "y": 3.5, "type": "ammo"}
    ]

# Raycasting function
def cast_ray(x, y, angle):
    angle = angle % (2 * math.pi)
    dx = math.cos(angle)
    dy = math.sin(angle)
    map_x = int(x)
    map_y = int(y)
    delta_dist_x = abs(1 / dx) if dx != 0 else float('inf')
    delta_dist_y = abs(1 / dy) if dy != 0 else float('inf')
    if dx > 0:
        step_x = 1
        side_dist_x = (map_x + 1 - x) * delta_dist_x
    else:
        step_x = -1
        side_dist_x = (x - map_x) * delta_dist_x
    if dy > 0:
        step_y = 1
        side_dist_y = (map_y + 1 - y) * delta_dist_y
    else:
        step_y = -1
        side_dist_y = (y - map_y) * delta_dist_y
    while True:
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x
            map_x += step_x
            side = 0
        else:
            side_dist_y += delta_dist_y
            map_y += step_y
            side = 1
        if MAP[map_y][map_x] == 1:
            if side == 0:
                distance = side_dist_x - delta_dist_x
            else:
                distance = side_dist_y - delta_dist_y
            return distance

# Project enemy positions
def project_enemy(enemy, player_x, player_y, player_angle):
    dx = enemy["x"] - player_x
    dy = enemy["y"] - player_y
    distance = math.sqrt(dx**2 + dy**2)
    if distance == 0:
        return None
    enemy_angle = math.atan2(dy, dx)
    angle_diff = (enemy_angle - player_angle) % (2 * math.pi)
    if angle_diff > math.pi:
        angle_diff -= 2 * math.pi
    if abs(angle_diff) > FOV / 2:
        return None
    screen_x = WIDTH / 2 + (angle_diff / (FOV / 2)) * (WIDTH / 2)
    enemy_screen_height = HEIGHT / distance
    if enemy["type"] == "boss":
        enemy_screen_height *= 2
    enemy_screen_width = enemy_screen_height
    return screen_x, enemy_screen_height, enemy_screen_width, distance

# Project powerup positions
def project_powerup(powerup, player_x, player_y, player_angle):
    dx = powerup["x"] - player_x
    dy = powerup["y"] - player_y
    distance = math.sqrt(dx**2 + dy**2)
    if distance == 0:
        return None
    powerup_angle = math.atan2(dy, dx)
    angle_diff = (powerup_angle - player_angle) % (2 * math.pi)
    if angle_diff > math.pi:
        angle_diff -= 2 * math.pi
    if abs(angle_diff) > FOV / 2:
        return None
    screen_x = WIDTH / 2 + (angle_diff / (FOV / 2)) * (WIDTH / 2)
    powerup_screen_height = HEIGHT / distance * 0.5
    powerup_screen_width = powerup_screen_height
    return screen_x, powerup_screen_height, powerup_screen_width, distance

# Move enemies
def move_enemy(enemy, player_x, player_y):
    if enemy["type"] == "boss": speed = BOSS_SPEED
    elif enemy["type"] == "fast": speed = FAST_SPEED
    else: speed = REGULAR_SPEED
    dx = player_x - enemy["x"]
    dy = player_y - enemy["y"]
    distance = math.sqrt(dx**2 + dy**2)
    if distance > 0:
        dx /= distance
        dy /= distance
        new_x = enemy["x"] + dx * speed
        new_y = enemy["y"] + dy * speed
        if MAP[int(new_y)][int(new_x)] == 0:
            enemy["x"] = new_x
            enemy["y"] = new_y

# Shooting mechanics
def shoot(player_x, player_y, player_angle, wall_distances):
    global player_ammo, game_state
    if player_ammo > 0:
        player_ammo -= 1
        wall_distance = wall_distances[NUM_RAYS // 2]
        candidates = []
        for enemy in enemies:
            dx = enemy["x"] - player_x
            dy = enemy["y"] - player_y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0 and distance < wall_distance:
                enemy_angle = math.atan2(dy, dx)
                angle_diff = (enemy_angle - player_angle) % (2 * math.pi)
                if angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                if abs(angle_diff) < 0.1:
                    candidates.append((distance, enemy))
        if candidates:
            candidates.sort(key=lambda c: c[0])
            _, hit_enemy = candidates[0]
            hit_enemy["health"] -= 1
            if hit_enemy["health"] <= 0:
                enemies.remove(hit_enemy)
                if hit_enemy["type"] == "boss":
                    game_state = GAME_OVER

# Mini-map (scaled to 100x100 for 20x20 map)
def draw_minimap():
    pygame.draw.rect(screen, (0, 0, 0), (700, 0, 100, 100))
    for row in range(20):
        for col in range(20):
            if MAP[row][col] == 1:
                pygame.draw.rect(screen, (100, 100, 100), (700 + col * 5, row * 5, 5, 5))
    pygame.draw.rect(screen, (0, 255, 0), (700 + player_x * 5 - 2, player_y * 5 - 2, 4, 4))
    for enemy in enemies:
        if enemy["type"] == "boss": color = (255, 0, 0) 
        if enemy["type"] == "regular": color = (0, 0, 255) 
        else: color = (255, 255, 0) 
        pygame.draw.rect(screen, color, (700 + enemy["x"] * 5 - 2, enemy["y"] * 5 - 2, 4, 4))
    for powerup in powerups:
        color = (0, 255, 0) if powerup["type"] == "health" else (0, 0, 0)
        pygame.draw.rect(screen, color, (700 + powerup["x"] * 5 - 1, powerup["y"] * 5 - 1, 2, 2))
    pygame.draw.rect(screen, (255, 255, 255), (700, 0, 100, 100), 1)

# Menu rendering functions
def draw_main_menu():
    screen.fill((0, 0, 0))
    title = title_font.render("Maze Shooter", True, (255, 255, 255))
    start_text = font.render("Press SPACE to Start", True, (255, 255, 255))
    quit_text = font.render("Press ESC to Quit", True, (255, 255, 255))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
    screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 50))
    pygame.display.flip()

def draw_game_over(won=False):
    screen.fill((0, 0, 0))
    result_text = title_font.render("You Win!" if won else "Game Over", True, (255, 255, 255))
    restart_text = font.render("Press SPACE to Restart", True, (255, 255, 255))
    quit_text = font.render("Press ESC to Quit", True, (255, 255, 255))
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//4))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2))
    screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 50))
    pygame.display.flip()

# Setup
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
clock = pygame.time.Clock()
running = True

# Initial player setup
reset_player()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                if game_state in [MAIN_MENU, GAME_OVER]:
                    reset_player()
                    game_state = PLAYING
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
        elif event.type == pygame.MOUSEBUTTONDOWN and game_state == PLAYING:
            if event.button == 1:
                shoot(player_x, player_y, player_angle, wall_distances)

    if game_state == MAIN_MENU:
        draw_main_menu()
        
    elif game_state == PLAYING:
        keys = pygame.key.get_pressed()

        # Player rotation
        mouse_dx, _ = pygame.mouse.get_rel()
        player_angle += mouse_dx * MOUSE_SENSITIVITY
        if keys[pygame.K_LEFT]:
            player_angle -= 0.02
        if keys[pygame.K_RIGHT]:
            player_angle += 0.02
        player_angle %= 2 * math.pi

        # Player movement with WASD and arrows
        dx = math.cos(player_angle)
        dy = math.sin(player_angle)
        strafe_dx = -math.sin(player_angle)
        strafe_dy = math.cos(player_angle)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_x = player_x + MOVE_SPEED * dx
            new_y = player_y + MOVE_SPEED * dy
            if MAP[int(new_y)][int(new_x)] == 0:
                player_x = new_x
                player_y = new_y
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_x = player_x - MOVE_SPEED * dx
            new_y = player_y - MOVE_SPEED * dy
            if MAP[int(new_y)][int(new_x)] == 0:
                player_x = new_x
                player_y = new_y
        if keys[pygame.K_a]:
            new_x = player_x + MOVE_SPEED * strafe_dx
            new_y = player_y + MOVE_SPEED * strafe_dy
            if MAP[int(new_y)][int(new_x)] == 0:
                player_x = new_x
                player_y = new_y
        if keys[pygame.K_d]:
            new_x = player_x + MOVE_SPEED * -strafe_dx
            new_y = player_y + MOVE_SPEED * -strafe_dy
            if MAP[int(new_y)][int(new_x)] == 0:
                player_x = new_x
                player_y = new_y

        # Check for powerup pickups
        to_remove = []
        for powerup in powerups:
            dx = player_x - powerup["x"]
            dy = player_y - powerup["y"]
            distance = math.sqrt(dx**2 + dy**2)
            if distance < 0.5:
                if powerup["type"] == "health":
                    player_health = min(100, player_health + 20)
                elif powerup["type"] == "ammo":
                    player_ammo += 10
                to_remove.append(powerup)
        for powerup in to_remove:
            powerups.remove(powerup)

        # Compute wall distances
        wall_distances = []
        for col in range(NUM_RAYS):
            ray_angle = player_angle - FOV / 2 + (col / NUM_RAYS) * FOV
            distance = cast_ray(player_x, player_y, ray_angle)
            wall_distances.append(distance)

        # Move enemies and spawn new ones
        current_time = pygame.time.get_ticks()
        for enemy in enemies:
            move_enemy(enemy, player_x, player_y)
            if enemy["type"] == "boss" and current_time - enemy["last_spawn_time"] > 7000:
                for offset in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                    new_col = int(enemy["x"]) + offset[0]
                    new_row = int(enemy["y"]) + offset[1]
                    if 0 <= new_row < 20 and 0 <= new_col < 20 and MAP[new_row][new_col] == 0:
                        enemies.append({"x": new_col + 0.5, "y": new_row + 0.5, "type": "regular", "health": 5, "max_health": 5})
                        enemies.append({"x": new_col + 0.5, "y": new_row + 0.5, "type": "fast", "health": 3, "max_health": 3})
                enemy["last_spawn_time"] = current_time

        # Enemy attacks
        for enemy in enemies:
            dx = player_x - enemy["x"]
            dy = player_y - enemy["y"]
            distance = math.sqrt(dx**2 + dy**2)
            if distance < 0.5:
                player_health -= 0.1

        # Check game over
        if player_health <= 0:
            game_state = GAME_OVER

        # Rendering
        pygame.draw.rect(screen, (40, 40, 255), (0, 0, WIDTH, HEIGHT / 2))
        # pygame.draw.rect(screen, (0, 255, 0), (0, HEIGHT / 2, WIDTH, HEIGHT / 2))
        # pygame.draw.rect(screen, (255, 165, 0), (0, 0, WIDTH, HEIGHT / 2))  # Orange sky
        pygame.draw.rect(screen, (139, 69, 19), (0, HEIGHT / 2, WIDTH, HEIGHT / 2))
        # Draw walls
        for col in range(NUM_RAYS):
            distance = wall_distances[col]
            wall_height = HEIGHT / (distance + 0.0001)
            shade = max(0, 255 - distance * 30)
            color = (shade, shade, shade)
            pygame.draw.line(screen, color, (col, HEIGHT / 2 - wall_height / 2), (col, HEIGHT / 2 + wall_height / 2))

        # Draw enemies with health bars
        visible_enemies = []
        for enemy in enemies:
            projection = project_enemy(enemy, player_x, player_y, player_angle)
            if projection:
                screen_x, enemy_screen_height, enemy_screen_width, distance = projection
                ray_index = int(screen_x + 0.5)
                if 0 <= ray_index < NUM_RAYS and distance < wall_distances[ray_index]:
                    visible_enemies.append((screen_x, enemy_screen_height, enemy_screen_width, distance, enemy))
        visible_enemies.sort(key=lambda e: e[3], reverse=True)
        for screen_x, enemy_screen_height, enemy_screen_width, distance, enemy in visible_enemies:
            if enemy["type"] == "boss": color = (255, 0, 0) 
            if enemy["type"] == "regular": color = (0, 0, 255) 
            else: color = (255, 255, 0) 



            top = HEIGHT / 2 - enemy_screen_height / 2
            left = screen_x - enemy_screen_width / 2
            pygame.draw.rect(screen, color, (left, top, enemy_screen_width, enemy_screen_height))
            # Draw health bar
            health_ratio = enemy["health"] / enemy["max_health"]
            bar_width = enemy_screen_width * health_ratio
            bar_height = 5
            pygame.draw.rect(screen, (255, 0, 0), (left, top - bar_height - 2, enemy_screen_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (left, top - bar_height - 2, bar_width, bar_height))

        # Draw powerups
        visible_powerups = []
        for powerup in powerups:
            projection = project_powerup(powerup, player_x, player_y, player_angle)
            if projection:
                screen_x, powerup_screen_height, powerup_screen_width, distance = projection
                ray_index = int(screen_x + 0.5)
                if 0 <= ray_index < NUM_RAYS and distance < wall_distances[ray_index]:
                    visible_powerups.append((screen_x, powerup_screen_height, powerup_screen_width, distance, powerup))
        visible_powerups.sort(key=lambda p: p[3], reverse=True)
        for screen_x, powerup_screen_height, powerup_screen_width, distance, powerup in visible_powerups:
            color = (0, 255, 0) if powerup["type"] == "health" else (255, 255, 0)
            top = HEIGHT / 2 - powerup_screen_height / 2
            left = screen_x - powerup_screen_width / 2
            pygame.draw.rect(screen, color, (left, top, powerup_screen_width, powerup_screen_height))

        ammo_text = font.render(f"Ammo: {player_ammo}", True, (255, 255, 255))
        pygame.draw.rect(screen, (255, 0, 0), (10, 15, 200, 25))
        pygame.draw.rect(screen, (0, 255, 0), (10, 15, 2*player_health, 25))
        screen.blit(ammo_text, (10, 50))

        # Draw crosshair
        pygame.draw.line(screen, (255, 255, 255), (WIDTH / 2 - 10, HEIGHT / 2), (WIDTH / 2 + 10, HEIGHT / 2), 2)
        pygame.draw.line(screen, (255, 255, 255), (WIDTH / 2, HEIGHT / 2 - 10), (WIDTH / 2, HEIGHT / 2 + 10), 2)

        # Draw minimap
        draw_minimap()

        pygame.display.flip()

    elif game_state == GAME_OVER:
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        won = not enemies or not any(e["type"] == "boss" for e in enemies)
        draw_game_over(won)

    clock.tick(60)

pygame.quit()