import pygame
import math
import time
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Shooter")

# Game constants
FOV = 60 * (math.pi / 180)
NUM_RAYS = WIDTH
MOVE_SPEED = 3
MOUSE_SENSITIVITY = 0.002
MAX_SPRITE_SIZE = 500

# Enemy speeds
BOSS_SPEED = 0.5
REGULAR_SPEED = .8
FAST_SPEED = 3
FIREBALL_SPEED = 10

# Load sprites
enemy_sprites = {
    "boss": pygame.image.load("boss.png").convert_alpha(),
    "regular": pygame.image.load("regular.png").convert_alpha(),
    "fast": pygame.image.load("fast.png").convert_alpha(),
    "fireball": pygame.image.load("fireball.png").convert_alpha()
}

deltaTime = 0

MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1],
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
    [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)

# Game states
MAIN_MENU, PLAYING, GAME_OVER = 0, 1, 2
game_state = MAIN_MENU

# Player variables
def reset_player():
    global player_x, player_y, player_angle, player_health, player_ammo, enemies, powerups, fireballs
    player_x = 1.5
    player_y = 1.5
    player_angle = 0
    player_health = 100
    player_ammo = 100
    enemies = [
        {"x": 1, "y": 18, "type": "regular", "health": 10, "max_health": 10},
        {"x": 7.5, "y": 5.5, "type": "regular", "health": 10, "max_health": 10},
        {"x": 18.5, "y": 18.5, "type": "boss", "health": 70, "max_health": 70, "last_spawn_time": 0, "last_fireball_time": 0}
    ]
    powerups = [
        {"x": 5.5, "y": 5.5, "type": "health"},
        {"x": 12.5, "y": 11.5, "type": "health"},
        {"x": 1, "y": 17, "type": "ammo"},
        {"x": 16.5, "y": 18.5, "type": "ammo"}
    ]
    fireballs = []

def cast_ray(x, y, angle):
    angle %= 2 * math.pi
    dx, dy = math.cos(angle), math.sin(angle)
    map_x, map_y = int(x), int(y)
    delta_dist_x = abs(1 / dx) if dx != 0 else float('inf')
    delta_dist_y = abs(1 / dy) if dy != 0 else float('inf')
    step_x = 1 if dx > 0 else -1
    step_y = 1 if dy > 0 else -1
    side_dist_x = (map_x + 1 - x if dx > 0 else x - map_x) * delta_dist_x
    side_dist_y = (map_y + 1 - y if dy > 0 else y - map_y) * delta_dist_y
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
            return side_dist_x - delta_dist_x if side == 0 else side_dist_y - delta_dist_y

def project_sprite(obj, player_x, player_y, player_angle, sprite_type, scale_factor=1):
    dx = obj["x"] - player_x
    dy = obj["y"] - player_y
    distance = math.sqrt(dx**2 + dy**2)
    if distance < 0.1:
        return None
    angle_diff = (math.atan2(dy, dx) - player_angle) % (2 * math.pi)
    if angle_diff > math.pi:
        angle_diff -= 2 * math.pi
    if abs(angle_diff) > FOV / 2:
        return None
    screen_x = WIDTH / 2 + (angle_diff / (FOV / 2)) * (WIDTH / 2)
    height = min(MAX_SPRITE_SIZE, HEIGHT / distance * scale_factor)
    sprite = enemy_sprites[sprite_type]
    aspect = sprite.get_width() / sprite.get_height()
    width = min(MAX_SPRITE_SIZE, height * aspect)
    scaled_sprite = pygame.transform.scale(sprite, (int(width), int(height)))
    return screen_x, width, distance, scaled_sprite

def move_enemy(enemy, player_x, player_y):
    speed = {"boss": BOSS_SPEED, "fast": FAST_SPEED}.get(enemy["type"], REGULAR_SPEED)
    dx = player_x - enemy["x"]
    dy = player_y - enemy["y"]
    distance = math.sqrt(dx**2 + dy**2)
    if distance <0.2:pass
    elif distance > 0:
        dx /= distance
        dy /= distance
        new_x, new_y = enemy["x"] + dx * speed * deltaTime, enemy["y"] + dy * speed * deltaTime
        if MAP[int(new_y)][int(new_x)] == 0:
            enemy["x"], enemy["y"] = new_x, new_y
    

def move_fireball(fireball):
    fireball["x"] += math.cos(fireball["angle"]) * FIREBALL_SPEED * deltaTime
    fireball["y"] += math.sin(fireball["angle"]) * FIREBALL_SPEED * deltaTime
    return MAP[int(fireball["y"])][int(fireball["x"])] != 1

def shoot(player_x, player_y, player_angle, wall_distances):
    global player_ammo, game_state
    if player_ammo > 0:
        player_ammo -= 1
        wall_distance = wall_distances[WIDTH // 2]
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

def draw_minimap():
    pygame.draw.rect(screen, (0, 0, 0), (700, 0, 100, 100))
    for row in range(20):
        for col in range(20):
            if MAP[row][col] == 1:
                pygame.draw.rect(screen, (100, 100, 100), (700 + col * 5, row * 5, 5, 5))
    pygame.draw.rect(screen, (0, 255, 0), (700 + player_x * 5 - 2, player_y * 5 - 2, 4, 4))
    for enemy in enemies:
        color = {"boss": (255, 0, 0), "regular": (0, 0, 255), "fast": (255, 255, 0)}[enemy["type"]]
        pygame.draw.rect(screen, color, (700 + enemy["x"] * 5 - 2, enemy["y"] * 5 - 2, 4, 4))
    for powerup in powerups:
        color = (0, 255, 0) if powerup["type"] == "health" else (255, 255, 0)
        pygame.draw.rect(screen, color, (700 + powerup["x"] * 5 - 1, powerup["y"] * 5 - 1, 2, 2))
    pygame.draw.rect(screen, (255, 255, 255), (700, 0, 100, 100), 1)

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
reset_player()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE and game_state in [MAIN_MENU, GAME_OVER]:
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
        player_angle %= 2 * math.pi

        # Player movement
        dx, dy = math.cos(player_angle), math.sin(player_angle)
        strafe_dx, strafe_dy = -math.sin(player_angle), math.cos(player_angle)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_x, new_y = player_x + MOVE_SPEED * dx * deltaTime, player_y + MOVE_SPEED * dy * deltaTime
            if MAP[int(new_y)][int(new_x)] == 0:
                player_x, player_y = new_x, new_y
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_x, new_y = player_x - MOVE_SPEED * dx * deltaTime, player_y - MOVE_SPEED * dy * deltaTime
            if MAP[int(new_y)][int(new_x)] == 0:
                player_x, player_y = new_x, new_y
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            new_x, new_y = player_x + MOVE_SPEED * strafe_dx * deltaTime, player_y + MOVE_SPEED * strafe_dy * deltaTime
            if MAP[int(new_y)][int(new_x)] == 0:
                player_x, player_y = new_x, new_y
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            new_x, new_y = player_x - MOVE_SPEED * strafe_dx * deltaTime, player_y - MOVE_SPEED * strafe_dy * deltaTime
            if MAP[int(new_y)][int(new_x)] == 0:
                player_x, player_y = new_x, new_y

        # Powerup pickups
        to_remove = [p for p in powerups if math.hypot(player_x - p["x"], player_y - p["y"]) < 0.5]
        for powerup in to_remove:
            if powerup["type"] == "health":
                player_health = 100
            elif powerup["type"] == "ammo":
                player_ammo += 100
            powerups.remove(powerup)

        # Compute wall distances
        wall_distances = [cast_ray(player_x, player_y, player_angle - FOV / 2 + (col / NUM_RAYS) * FOV) for col in range(NUM_RAYS)]

        # Update enemies and fireballs
        current_time = pygame.time.get_ticks()
        for enemy in enemies[:]:
            move_enemy(enemy, player_x, player_y)
            if enemy["type"] == "boss":
                if current_time - enemy["last_fireball_time"] > 5000:
                    dx, dy = player_x - enemy["x"], player_y - enemy["y"]
                    distance = math.hypot(dx, dy)
                    if distance > 0:
                        fireballs.append({"x": enemy["x"], "y": enemy["y"], "angle": math.atan2(dy, dx)})
                        enemy["last_fireball_time"] = current_time
                if current_time - enemy["last_spawn_time"] > 10000:
                    for offset in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                        new_col, new_row = int(enemy["x"]) + offset[0], int(enemy["y"]) + offset[1]
                        if 0 <= new_row < 20 and 0 <= new_col < 20 and MAP[new_row][new_col] == 0:
                            spawnable_enemies = [
                                {"x": new_col + 0.5, "y": new_row + 0.5, "type": "regular", "health": 5, "max_health": 5},
                                {"x": new_col + 0.5, "y": new_row + 0.5, "type": "fast", "health": 3, "max_health": 3}
                            ]
                            if len(enemies) < 7: enemies.extend([random.choice(spawnable_enemies)])
                    enemy["last_spawn_time"] = current_time

        # Update fireballs
        to_remove = []
        for fireball in fireballs[:]:
            if not move_fireball(fireball):
                to_remove.append(fireball)
            elif math.hypot(player_x - fireball["x"], player_y - fireball["y"]) < 0.5:
                player_health -= 25
                to_remove.append(fireball)
        for fireball in to_remove:
            if fireball in fireballs:
                fireballs.remove(fireball)

        # Enemy attacks
        for enemy in enemies:
            if math.hypot(player_x - enemy["x"], player_y - enemy["y"]) < 0.5: 
                if enemy['type'] != 'boss':    
                    player_health -= 0.1
                else:
                    player_health -= 1

        # Check game over
        if player_health <= 0:
            game_state = GAME_OVER

        pygame.draw.rect(screen, (30, 30, 30), (0, 0, WIDTH, HEIGHT / 2))  # black Sky
        pygame.draw.rect(screen, (0, 0, 0), (0, HEIGHT / 2, WIDTH, HEIGHT / 2))  # kinda black Ground

        # Draw walls (fixed to avoid gaps)
        for col, distance in enumerate(wall_distances):
            wall_height = HEIGHT / (distance + 0.0001)
            shade = max(0, 100 - distance * 10)
            color = (shade, shade, shade)
            pygame.draw.line(screen, color, (col, HEIGHT / 2 - wall_height / 2), (col, HEIGHT / 2 + wall_height / 2))

        # Draw enemies
        visible_enemies = []
        for enemy in enemies:
            projection = project_sprite(enemy, player_x, player_y, player_angle, enemy["type"], 2 if enemy["type"] == "boss" else 1)
            if projection:
                screen_x, width, distance, sprite = projection
                if 0 <= int(screen_x) < NUM_RAYS and distance < wall_distances[int(screen_x)]:
                    visible_enemies.append((screen_x, width, distance, enemy, sprite))
        visible_enemies.sort(key=lambda e: e[2], reverse=True)
        for screen_x, width, _, enemy, sprite in visible_enemies:
            top = HEIGHT / 2 - sprite.get_height() / 2
            left = screen_x - width / 2
            screen.blit(sprite, (left, top))
            health_ratio = enemy["health"] / enemy["max_health"]
            bar_width = width * health_ratio
            pygame.draw.rect(screen, (255, 0, 0), (left, top - 7, width, 5))
            pygame.draw.rect(screen, (0, 255, 0), (left, top - 7, bar_width, 5))

        # Draw fireballs
        visible_fireballs = [proj for f in fireballs if (proj := project_sprite(f, player_x, player_y, player_angle, "fireball", 0.5))]
        visible_fireballs.sort(key=lambda f: f[2], reverse=True)
        for screen_x, width, distance, sprite in visible_fireballs:
            if 0 <= int(screen_x) < NUM_RAYS and distance < wall_distances[int(screen_x)]:
                screen.blit(sprite, (screen_x - width / 2, HEIGHT / 2 - sprite.get_height() / 2))

        # Draw powerups
        visible_powerups = []
        for powerup in powerups:
            dx, dy = powerup["x"] - player_x, powerup["y"] - player_y
            distance = math.hypot(dx, dy)
            if distance > 0 and abs((math.atan2(dy, dx) - player_angle) % (2 * math.pi)) <= FOV / 2:
                screen_x = WIDTH / 2 + ((math.atan2(dy, dx) - player_angle) / (FOV / 2)) * (WIDTH / 2)
                size = min(MAX_SPRITE_SIZE, HEIGHT / distance * 0.5)
                if 0 <= int(screen_x) < NUM_RAYS and distance < wall_distances[int(screen_x)]:
                    visible_powerups.append((screen_x, size, distance, powerup))
        visible_powerups.sort(key=lambda p: p[2], reverse=True)
        for screen_x, size, _, powerup in visible_powerups:
            color = (0, 255, 0) if powerup["type"] == "health" else (255, 255, 0)
            pygame.draw.rect(screen, color, (screen_x - size / 2, HEIGHT / 2 - size / 2, size, size))

        # HUD
        pygame.draw.rect(screen, (255, 0, 0), (10, 15, 200, 25))
        pygame.draw.rect(screen, (0, 255, 0), (10, 15, 2 * player_health, 25))
        screen.blit(font.render(f"Ammo: {player_ammo}", True, (255, 255, 255)), (10, 50))

        # Crosshair
        pygame.draw.line(screen, (255, 255, 255), (WIDTH / 2 - 10, HEIGHT / 2), (WIDTH / 2 + 10, HEIGHT / 2), 2)
        pygame.draw.line(screen, (255, 255, 255), (WIDTH / 2, HEIGHT / 2 - 10), (WIDTH / 2, HEIGHT / 2 + 10), 2)

        draw_minimap()
        pygame.display.flip()

    elif game_state == GAME_OVER:
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        draw_game_over(not enemies or not any(e["type"] == "boss" for e in enemies))

    deltaTime = clock.tick(60) / 1000

pygame.quit()