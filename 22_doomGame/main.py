import pygame
import numpy as np
import math
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions and setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyGame Doom")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 150)
GRAY = (0, 100, 100)
DARK_GRAY = (50, 50, 50)
BROWN = (239, 69, 19)

# Constants
FOV = math.pi / 3  # 60 degrees field of view
HALF_FOV = FOV / 2
NUM_RAYS = 200  # Increased for smoother walls
MAX_DEPTH = 20
DELTA_ANGLE = FOV / NUM_RAYS
DIST = NUM_RAYS / (2 * math.tan(HALF_FOV))
PROJ_COEFF = HEIGHT * 2  # Adjusted for consistent wall height scaling
SCALE = WIDTH // NUM_RAYS  # 4 pixels per ray for WIDTH=800, NUM_RAYS=200
PLAYER_SPEED = 0.05
MOUSE_SENSITIVITY = 0.002
ENEMY_SPEED = 0.02
BOSS_SPEED = 0.01

# Maze class with recursive backtracking for maze-like structure
class Maze:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.maze = np.ones((height, width), dtype=int)  # 1 = wall, 0 = floor
        self.enemies = []
        self.boss = None
        self.generate_maze()
    
    def generate_maze(self):
        # Initialize all cells as walls
        for y in range(self.height):
            for x in range(self.width):
                self.maze[y][x] = 1
        
        # Use recursive backtracking to create maze
        def carve_path(x, y):
            self.maze[y][x] = 0  # Set current cell as path
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]  # Possible moves (down, right, up, left)
            random.shuffle(directions)
            
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self.width and 0 <= new_y < self.height and 
                    self.maze[new_y][new_x] == 1):
                    # Carve path by setting the wall between current and new cell to 0
                    wall_x, wall_y = x + dx // 2, y + dy // 2
                    self.maze[wall_y][wall_x] = 0
                    self.maze[new_y][new_x] = 0
                    carve_path(new_x, new_y)
        
        # Start from (1,1) to ensure even indices (avoiding edges)
        carve_path(1, 1)
        
        # Ensure player starting area is clear
        for y in range(1, 3):
            for x in range(1, 3):
                self.maze[y][x] = 0
        
        # Create boss room at far end
        boss_room_x, boss_room_y = self.width - 3, self.height - 3
        for y in range(boss_room_y - 1, boss_room_y + 2):
            for x in range(boss_room_x - 1, boss_room_x + 2):
                if 0 <= y < self.height and 0 <= x < self.width:
                    self.maze[y][x] = 0
        
        # Place boss
        self.boss = {'x': boss_room_x, 'y': boss_room_y, 'health': 500, 'type': 'boss'}
        
        # Add enemies along paths
        self.add_enemies(5)
    
    def add_enemies(self, count):
        for _ in range(count):
            while True:
                x = random.randint(3, self.width - 4)
                y = random.randint(3, self.height - 4)
                if self.maze[y][x] == 0 and not any(e['x'] == x and e['y'] == y for e in self.enemies):
                    # Ensure enemy is placed in a path, not near walls or player start
                    if (self.maze[y-1][x] == 0 or self.maze[y+1][x] == 0 or 
                        self.maze[y][x-1] == 0 or self.maze[y][x+1] == 0):
                        self.enemies.append({'x': x, 'y': y, 'health': 100, 'type': 'normal'})
                        break
    
    def is_wall(self, x, y):
        ix, iy = int(x), int(y)
        if 0 <= ix < self.width and 0 <= iy < self.height:
            return self.maze[iy][ix] == 1
        return True

    def update_enemies(self, player_x, player_y):
        for enemy in self.enemies[:]:  # Use slice to avoid runtime modifications
            dx = player_x - enemy['x']
            dy = player_y - enemy['y']
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0.5:  # Avoid getting stuck
                dx /= distance
                dy /= distance
                
                new_x = enemy['x'] + dx * ENEMY_SPEED
                new_y = enemy['y'] + dy * ENEMY_SPEED
                
                if not self.is_wall(new_x, new_y):
                    enemy['x'] = new_x
                    enemy['y'] = new_y
        
        if self.boss and self.boss['health'] > 0:
            dx = player_x - self.boss['x']
            dy = player_y - self.boss['y']
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 1.0:  # Boss keeps more distance
                dx /= distance
                dy /= distance
                
                new_x = self.boss['x'] + dx * BOSS_SPEED
                new_y = self.boss['y'] + dy * BOSS_SPEED
                
                if not self.is_wall(new_x, new_y):
                    self.boss['x'] = new_x
                    self.boss['y'] = new_y

# Player class to handle movement, raycasting, and shooting
class Player:
    def __init__(self, x=2.0, y=2.0):
        self.x = x
        self.y = y
        self.angle = 0
        self.health = 100
        self.ammo = 50
        self.last_shot_time = 0
    
    def move(self, maze):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        
        keys = pygame.key.get_pressed()
        moved = False
        
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            nx = self.x + PLAYER_SPEED * cos_a
            ny = self.y + PLAYER_SPEED * sin_a
            if not maze.is_wall(nx, ny):
                self.x, self.y = nx, ny
                moved = True
                
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            nx = self.x - PLAYER_SPEED * cos_a
            ny = self.y - PLAYER_SPEED * sin_a
            if not maze.is_wall(nx, ny):
                self.x, self.y = nx, ny
                moved = True
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            nx = self.x - PLAYER_SPEED * sin_a
            ny = self.y + PLAYER_SPEED * cos_a
            if not maze.is_wall(nx, ny):
                self.x, self.y = nx, ny
                moved = True
                
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            nx = self.x + PLAYER_SPEED * sin_a
            ny = self.y - PLAYER_SPEED * cos_a
            if not maze.is_wall(nx, ny):
                self.x, self.y = nx, ny
                moved = True
        
        return moved
        
    def update_mouse_look(self):
        mouse_dx, _ = pygame.mouse.get_rel()
        self.angle += mouse_dx * MOUSE_SENSITIVITY
        self.angle %= 2 * math.pi  # Keep angle in [0, 2π)
    
    def dda_raycast(self, maze, ray_dir):
        pos_x, pos_y = self.x, self.y
        map_x, map_y = int(pos_x), int(pos_y)
        ray_dir_x, ray_dir_y = ray_dir

        # Avoid division by zero
        if ray_dir_x == 0:
            ray_dir_x = 1e-30
        if ray_dir_y == 0:
            ray_dir_y = 1e-30

        delta_dist_x = abs(1 / ray_dir_x)
        delta_dist_y = abs(1 / ray_dir_y)

        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (pos_x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - pos_x) * delta_dist_x

        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (pos_y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - pos_y) * delta_dist_y

        hit = False
        side = 0
        while not hit and (0 <= map_x < maze.width and 0 <= map_y < maze.height):
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            if maze.is_wall(map_x, map_y):
                hit = True

        if hit:
            if side == 0:
                dist = (map_x - pos_x + (1 - step_x) / 2) / ray_dir_x
            else:
                dist = (map_y - pos_y + (1 - step_y) / 2) / ray_dir_y
        else:
            dist = MAX_DEPTH

        return max(0, min(dist, MAX_DEPTH))

    def cast_rays(self, maze):
        walls = []
        depth_buffer = []  # Store wall distances for occlusion

        for ray_num in range(NUM_RAYS):
            ray_angle = self.angle - HALF_FOV + DELTA_ANGLE * ray_num
            ray_dir = (math.cos(ray_angle), math.sin(ray_angle))
            dist = self.dda_raycast(maze, ray_dir)

            # Wall height calculation with improved scaling
            wall_height = int(PROJ_COEFF / (dist + 0.1))  # Small offset to prevent division issues
            wall_height = min(wall_height, HEIGHT)  # Cap at screen height
            brightness = max(139 - int(dist * 5), 60)  # Adjust brightness for brownish-red shading
            wall_color = (brightness, max(69 - int(dist * 3), 20), max(19 - int(dist * 1), 10))  # Maintain brownish-red hue
            offset = (HEIGHT - wall_height) // 2

            # Store wall data
            walls.append((ray_num * SCALE, offset, SCALE, wall_height, wall_color, dist))
            # Populate depth buffer for each column (extend to cover all pixels in the column)
            for x in range(ray_num * SCALE, min((ray_num + 1) * SCALE, WIDTH)):
                depth_buffer.append(dist if dist < MAX_DEPTH else float('inf'))

        # Ensure depth_buffer matches screen width
        while len(depth_buffer) < WIDTH:
            depth_buffer.append(float('inf'))

        return walls, depth_buffer

    def shoot(self, maze):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < 250 or self.ammo <= 0:
            return False

        self.ammo -= 1
        self.last_shot_time = current_time

        hit = None
        hit_distance = float('inf')
        for depth in range(20):  # Check up to 20 units ahead
            target_x = self.x + depth * 0.5 * math.cos(self.angle)
            target_y = self.y + depth * 0.5 * math.sin(self.angle)
            
            if maze.is_wall(target_x, target_y):
                break
            
            for enemy in maze.enemies:
                distance = math.sqrt((target_x - enemy['x'])**2 + (target_y - enemy['y'])**2)
                if distance < 0.7 and distance < hit_distance:
                    hit = enemy
                    hit_distance = distance
            
            if maze.boss and maze.boss['health'] > 0:
                boss_distance = math.sqrt((target_x - maze.boss['x'])**2 + (target_y - maze.boss['y'])**2)
                if boss_distance < 1.5 and distance < hit_distance:
                    hit = maze.boss
                    hit_distance = boss_distance
        
        if hit:
            if hit['type'] == 'normal':
                hit['health'] -= 34
                if hit['health'] <= 0:
                    if hit in maze.enemies:
                        maze.enemies.remove(hit)
                    self.ammo += 5
            elif hit['type'] == 'boss':
                hit['health'] -= 25
            return True
            
        return False
    
    def check_enemy_damage(self, maze):
        # Check damage from enemies
        for enemy in maze.enemies:
            distance = math.sqrt((self.x - enemy['x'])**2 + (self.y - enemy['y'])**2)
            if distance < 1.2:  # Enemy attack range
                self.health -= 0.5  # Damage per frame when close
        
        # Check damage from boss
        if maze.boss and maze.boss['health'] > 0:
            distance = math.sqrt((self.x - maze.boss['x'])**2 + (self.y - maze.boss['y'])**2)
            if distance < 2.0:  # Boss attack range (larger)
                self.health -= 1.0  # Boss deals more damage per frame

# Rendering function
def render_game(screen, player, maze, walls, depth_buffer):
    # Clear screen and draw sky/floor
    screen.fill(BLACK)
    pygame.draw.rect(screen, DARK_BLUE, (0, 0, WIDTH, HEIGHT // 2))  # Sky
    pygame.draw.rect(screen, DARK_GRAY, (0, HEIGHT // 2, WIDTH, HEIGHT // 2))  # Floor
    
    # Draw walls
    for wall in walls:
        x, y, w, h, color, _ = wall
        pygame.draw.rect(screen, color, (x, y, w, h))
    
    # Draw enemies with occlusion check
    for enemy in maze.enemies:
        # Calculate relative position and distance
        rel_x = enemy['x'] - player.x
        rel_y = enemy['y'] - player.y
        distance = math.sqrt(rel_x**2 + rel_y**2)
        angle = math.atan2(rel_y, rel_x) - player.angle
        
        # Normalize angle to [-pi, pi]
        while angle < -math.pi:
            angle += 2 * math.pi
        while angle > math.pi:
            angle -= 2 * math.pi
        
        # Check if enemy is in view frustum
        if abs(angle) < HALF_FOV:
            # Calculate screen position
            screen_x = int((angle + HALF_FOV) / FOV * WIDTH)
            sprite_size = min(int(800 / max(distance, 0.1)), HEIGHT)
            sprite_x = int(screen_x - sprite_size / 2)
            sprite_y = int((HEIGHT - sprite_size) / 2)
            
            # Check occlusion using depth buffer
            visible = False
            left_x = max(0, sprite_x)
            right_x = min(WIDTH, sprite_x + sprite_size)
            for x in range(left_x, right_x):
                if distance < depth_buffer[x]:
                    visible = True
                    break
            
            if visible and distance > 0.5:  # Only draw if in front of player
                pygame.draw.rect(screen, RED, (sprite_x, sprite_y, sprite_size, sprite_size))
                # Health bar for enemy
                health_pct = enemy['health'] / 100
                health_bar_width = int(sprite_size * health_pct)
                pygame.draw.rect(screen, BLACK, (sprite_x, sprite_y - 10, sprite_size, 5))
                pygame.draw.rect(screen, GREEN, (sprite_x, sprite_y - 10, health_bar_width, 5))
    
    # Draw boss with occlusion check
    if maze.boss and maze.boss['health'] > 0:
        rel_x = maze.boss['x'] - player.x
        rel_y = maze.boss['y'] - player.y
        distance = math.sqrt(rel_x**2 + rel_y**2)
        angle = math.atan2(rel_y, rel_x) - player.angle
        
        while angle < -math.pi:
            angle += 2 * math.pi
        while angle > math.pi:
            angle -= 2 * math.pi
        
        if abs(angle) < HALF_FOV:
            screen_x = int((angle + HALF_FOV) / FOV * WIDTH)
            sprite_size = min(int(1600 / max(distance, 0.1)), HEIGHT * 1.5)
            sprite_x = int(screen_x - sprite_size / 2)
            sprite_y = int((HEIGHT - sprite_size) / 2)
            
            visible = False
            left_x = max(0, sprite_x)
            right_x = min(WIDTH, sprite_x + sprite_size)
            for x in range(left_x, right_x):
                if distance < depth_buffer[x]:
                    visible = True
                    break
            
            if visible and distance > 0.5:
                pygame.draw.rect(screen, (150, 0, 0), (sprite_x, sprite_y, sprite_size, sprite_size))
                # Health bar for boss
                health_pct = maze.boss['health'] / 500
                health_bar_width = int(sprite_size * health_pct)
                pygame.draw.rect(screen, BLACK, (sprite_x, sprite_y - 15, sprite_size, 10))
                pygame.draw.rect(screen, RED, (sprite_x, sprite_y - 15, health_bar_width, 10))
    
    # Draw weapon (gun)
    gun_rect = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 150, 50, 100)
    pygame.draw.rect(screen, GRAY, gun_rect)
    
    # Draw crosshair
    pygame.draw.line(screen, WHITE, (WIDTH // 2 - 10, HEIGHT // 2), (WIDTH // 2 + 10, HEIGHT // 2), 2)
    pygame.draw.line(screen, WHITE, (WIDTH // 2, HEIGHT // 2 - 10), (WIDTH // 2, HEIGHT // 2 + 10), 2)
    
    # Draw HUD
    health_width = int(200 * (player.health / 100))
    pygame.draw.rect(screen, GREEN, (20, HEIGHT - 40, health_width, 20))
    pygame.draw.rect(screen, RED, (20 + health_width, HEIGHT - 40, 200 - health_width, 20), 1)
    
    font = pygame.font.SysFont('Arial', 30)
    ammo_text = font.render(f"Ammo: {player.ammo}", True, WHITE)
    screen.blit(ammo_text, (20, HEIGHT - 80))
    
    # Minimap (improved to show entire 20x20 maze clearly)
    map_size = 150  # Increased size for better visibility
    map_surface = pygame.Surface((map_size, map_size))
    map_surface.fill(BLACK)
    
    # Scale to fit entire 20x20 map into 150x150 pixels
    scale = map_size / max(maze.width, maze.height)  # Use max to ensure both dimensions fit
    for y in range(maze.height):
        for x in range(maze.width):
            if maze.is_wall(x, y):
                map_surface.set_at((int(x * scale), int(y * scale)), WHITE)
    
    # Draw player on minimap
    player_map_x = int(player.x * scale)
    player_map_y = int(player.y * scale)
    if 0 <= player_map_x < map_size and 0 <= player_map_y < map_size:
        pygame.draw.circle(map_surface, GREEN, (player_map_x, player_map_y), 2)
        end_x = player_map_x + int(math.cos(player.angle) * 5)
        end_y = player_map_y + int(math.sin(player.angle) * 5)
        pygame.draw.line(map_surface, GREEN, (player_map_x, player_map_y), (end_x, end_y), 1)
    
    # Draw enemies on minimap
    for enemy in maze.enemies:
        enemy_map_x = int(enemy['x'] * scale)
        enemy_map_y = int(enemy['y'] * scale)
        if 0 <= enemy_map_x < map_size and 0 <= enemy_map_y < map_size:
            pygame.draw.circle(map_surface, RED, (enemy_map_x, enemy_map_y), 1)
    
    # Draw boss on minimap
    if maze.boss:
        boss_map_x = int(maze.boss['x'] * scale)
        boss_map_y = int(maze.boss['y'] * scale)
        if 0 <= boss_map_x < map_size and 0 <= boss_map_y < map_size:
            pygame.draw.circle(map_surface, (200, 0, 0), (boss_map_x, boss_map_y), 3)
    
    # Display minimap at top-right corner
    screen.blit(map_surface, (WIDTH - map_size - 10, 10))
    pygame.draw.rect(screen, WHITE, (WIDTH - map_size - 10, 10, map_size, map_size), 1)

def main():
    maze = Maze(20, 20)
    player = Player()
    
    # Initialize mouse for looking around
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    pygame.mouse.get_rel()  # Reset mouse movement
    
    # Game states
    game_over = False
    victory = False
    
    # Font for messages
    font = pygame.font.SysFont('Arial', 36)
    
    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle keyboard events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and (game_over or victory):
                    # Restart game
                    maze = Maze(20, 20)
                    player = Player()
                    game_over = False
                    victory = False
            
            # Handle mouse for shooting
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and not victory:
                if event.button == 1:  # Left mouse button
                    player.shoot(maze)
        
        if not game_over and not victory:
            # Update player position
            player.move(maze)
            
            # Update player view direction based on mouse
            player.update_mouse_look()
            
            # Update enemies with simple following logic
            maze.update_enemies(player.x, player.y)
            
            # Check for enemy damage to player
            player.check_enemy_damage(maze)
            
            # Check for game over
            if player.health <= 0:
                game_over = True
            
            # Check for victory
            if maze.boss and maze.boss['health'] <= 0:
                victory = True
        
        # Cast rays for walls and get depth buffer for occlusion
        walls, depth_buffer = player.cast_rays(maze)
        
        # Render game
        render_game(screen, player, maze, walls, depth_buffer)
        
        # Draw game over or victory message
        if game_over:
            game_over_text = font.render("GAME OVER - Press R to Restart", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
        
        if victory:
            victory_text = font.render("VICTORY! - Press R to Restart", True, GREEN)
            screen.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 2))
        
        # Update display
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS
    
    # Cleanup
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()