import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Game")
clock = pygame.time.Clock()

# Font for UI
font = pygame.font.SysFont(None, 36)

# Path for enemies (horizontal line at y=300)
path = [(0, 300), (100, 300), (200, 300), (300, 300), (400, 300), (500, 300), (600, 300), (700, 300), (800, 300)]

# Game variables
resources = 100
lives = 10
wave_number = 1
wave_enemies = []
spawn_timer = 0
spawn_interval = 1000  # ms
tower_costs = {'cannon': 50, 'flamethrower': 75, 'ice': 60, 'generator': 50}
generator_income = 5  # Passive income per generator per second
selected_tower_type = 'cannon'
game_over = False
win = False

# Sprite groups
enemy_group = pygame.sprite.Group()
tower_group = pygame.sprite.Group()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type):
        super().__init__()
        self.type = enemy_type
        if enemy_type == 'basic':
            self.image = pygame.Surface((20, 20))
            self.image.fill(RED)
            self.speed = 2
            self.health = 100
        elif enemy_type == 'fast':
            self.image = pygame.Surface((15, 15))
            self.image.fill(YELLOW)
            self.speed = 4
            self.health = 50
        elif enemy_type == 'tanky':
            self.image = pygame.Surface((30, 30))
            self.image.fill(GREEN)
            self.speed = 1
            self.health = 300
        elif enemy_type == 'boss':
            self.image = pygame.Surface((40, 40))
            self.image.fill(RED)
            self.speed = 1
            self.health = 1000
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(path[0])
        self.rect.center = self.pos
        self.waypoint_index = 0
        self.slow_timer = 0

    def update(self):
        global resources, lives
        speed = self.speed * (0.5 if self.slow_timer > 0 else 1)
        if self.slow_timer > 0:
            self.slow_timer -= 1
        if self.waypoint_index < len(path) - 1:
            target = pygame.math.Vector2(path[self.waypoint_index + 1])
            direction = target - self.pos
            distance = direction.length()
            if distance < speed:
                self.pos = target
                self.waypoint_index += 1
            else:
                direction.normalize_ip()
                self.pos += direction * speed
            self.rect.center = self.pos
        else:
            lives -= 1
            self.kill()

        if self.health <= 0:
            resources += {'basic': 10, 'fast': 15, 'tanky': 25, 'boss': 100}[self.type]
            self.kill()

# Tower class
class Tower(pygame.sprite.Sprite):
    def __init__(self, position, tower_type):
        super().__init__()
        self.type = tower_type
        self.level = 1
        self.position = position
        if tower_type == 'cannon':
            self.image = pygame.Surface((30, 30))
            self.image.fill(BLUE)
            self.range = 100
            self.damage = 20
            self.cooldown_max = 60
        elif tower_type == 'flamethrower':
            self.image = pygame.Surface((30, 30))
            self.image.fill(RED)
            self.range = 80
            self.damage = 10
            self.cooldown_max = 30
        elif tower_type == 'ice':
            self.image = pygame.Surface((30, 30))
            self.image.fill(WHITE)
            self.range = 90
            self.damage = 5
            self.cooldown_max = 45
        elif tower_type == 'generator':
            self.image = pygame.Surface((30, 30))
            self.image.fill(YELLOW)
            self.range = 0
            self.damage = 0
            self.cooldown_max = 60
        self.rect = self.image.get_rect(center=position)
        self.cooldown = 0
        self.target = None
        self.attack_timer = 0

    def update(self, enemies):
        if self.type == 'generator':
            global resources
            if self.cooldown <= 0:
                resources += generator_income
                self.cooldown = self.cooldown_max
            else:
                self.cooldown -= 1
            return

        if self.cooldown > 0:
            self.cooldown -= 1
        else:
            if self.type == 'cannon' or self.type == 'ice':
                target = self.find_target(enemies)
                if target:
                    if self.type == 'cannon':
                        if self.level >= 10 and random.random() < 0.2:  # Chain lightning
                            self.chain_lightning(target, enemies)
                        else:
                            target.health -= self.damage
                    elif self.type == 'ice':
                        target.health -= self.damage
                        target.slow_timer = 120  # 2 seconds at 60 FPS
                    self.cooldown = self.cooldown_max
                    self.target = target
                    self.attack_timer = 10
            elif self.type == 'flamethrower':
                targets = self.find_targets_aoe(enemies)
                if targets:
                    for target in targets:
                        if self.level >= 10 and random.random() < 0.2:  # Explosive shots
                            self.explosive_shot(target, enemies)
                        else:
                            target.health -= self.damage
                    self.cooldown = self.cooldown_max
                    self.attack_timer = 10

        if self.attack_timer > 0:
            self.attack_timer -= 1
        else:
            self.target = None

    def find_target(self, enemies):
        for enemy in enemies:
            distance = pygame.math.Vector2(enemy.rect.center).distance_to(self.rect.center)
            if distance < self.range:
                return enemy
        return None

    def find_targets_aoe(self, enemies):
        targets = []
        for enemy in enemies:
            if pygame.math.Vector2(enemy.rect.center).distance_to(self.rect.center) < self.range:
                targets.append(enemy)
        return targets

    def chain_lightning(self, target, enemies):
        targets_hit = [target]
        current = target
        for _ in range(2):  # Hits 3 enemies total
            next_target = None
            min_dist = float('inf')
            for enemy in enemies:
                if enemy not in targets_hit:
                    dist = pygame.math.Vector2(enemy.rect.center).distance_to(current.rect.center)
                    if dist < 80 and dist < min_dist:
                        min_dist = dist
                        next_target = enemy
            if next_target:
                targets_hit.append(next_target)
                current = next_target
        for enemy in targets_hit:
            enemy.health -= self.damage * 1.5

    def explosive_shot(self, target, enemies):
        for enemy in enemies:
            if pygame.math.Vector2(enemy.rect.center).distance_to(target.rect.center) < 50:
                enemy.health -= self.damage * 2

    def upgrade(self):
        if self.level < 10:
            cost = 20 * self.level
            global resources
            if resources >= cost:
                resources -= cost
                self.level += 1
                self.damage += 5
                self.range += 10
                self.cooldown_max = max(15, self.cooldown_max - 5)
                return True
        return False

# Wave definitions
def generate_wave(wave_num):
    if wave_num == 10:
        return [('boss', 0)]
    enemies = []
    for _ in range(wave_num * 2 + 5):
        r = random.random()
        if wave_num > 5 and r < 0.2:
            enemies.append(('tanky', len(enemies) * 0.5))
        elif wave_num > 3 and r < 0.4:
            enemies.append(('fast', len(enemies) * 0.5))
        else:
            enemies.append(('basic', len(enemies) * 0.5))
    if wave_num > 7:
        enemies.append(('tanky', len(enemies) * 0.5))  # Miniboss
    return enemies

# Endscreen function
def endscreen(win):
    screen.fill(BLACK)
    if win:
        text = font.render("You Win!", True, WHITE)
    else:
        text = font.render("Game Over", True, WHITE)
    screen.blit(text, (WIDTH // 2 - 50, HEIGHT // 2 - 20))
    pygame.display.flip()
    pygame.time.wait(3000)

# Check if position is valid for tower placement
def is_valid_position(pos):
    # Check screen boundaries (towers are 30x30, so 15 pixels from edges)
    if pos[0] < 15 or pos[0] > WIDTH - 15 or pos[1] < 15 or pos[1] > HEIGHT - 15:
        return False
    # Check if too close to path (y=280 to y=320 for largest enemy, adjust for tower height)
    if 265 < pos[1] < 335:
        return False
    # Check if too close to other towers
    for tower in tower_group:
        if pygame.math.Vector2(tower.rect.center).distance_to(pos) < 35:
            return False
    return True

# Main game loop
running = True
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            # Check if clicking on tower selection
            if 10 <= pos[0] <= 60 and 100 <= pos[1] <= 130:
                selected_tower_type = 'cannon'
            elif 70 <= pos[0] <= 120 and 100 <= pos[1] <= 130:
                selected_tower_type = 'flamethrower'
            elif 130 <= pos[0] <= 180 and 100 <= pos[1] <= 130:
                selected_tower_type = 'ice'
            elif 190 <= pos[0] <= 240 and 100 <= pos[1] <= 130:
                selected_tower_type = 'generator'
            else:
                # Check if clicking on an existing tower to upgrade
                for tower in tower_group:
                    if tower.rect.collidepoint(pos):
                        tower.upgrade()
                        break
                else:
                    # Place new tower if position is valid
                    if is_valid_position(pos) and resources >= tower_costs[selected_tower_type]:
                        tower = Tower(pos, selected_tower_type)
                        tower_group.add(tower)
                        resources -= tower_costs[selected_tower_type]

    # Spawn enemies
    if not wave_enemies and len(enemy_group) == 0 and wave_number <= 10:
        wave_enemies = generate_wave(wave_number)
        wave_number += 1
        spawn_timer = current_time
    if wave_enemies and current_time - spawn_timer >= spawn_interval * wave_enemies[0][1]:
        enemy_type, _ = wave_enemies.pop(0)
        enemy = Enemy(enemy_type)
        enemy_group.add(enemy)
        spawn_timer = current_time

    # Update
    enemy_group.update()
    tower_group.update(enemy_group)

    # Check for game over or victory
    if lives <= 0:
        game_over = True
    elif wave_number > 10 and len(enemy_group) == 0:
        win = True

    if game_over or win:
        endscreen(win)
        running = False

    # Draw
    screen.fill(BLACK)
    # Draw the enemy path
    for i in range(len(path) - 1):
        pygame.draw.line(screen, WHITE, path[i], path[i + 1], 5)
    tower_group.draw(screen)
    enemy_group.draw(screen)

    # Draw attack visuals
    for tower in tower_group:
        if tower.attack_timer > 0:
            if tower.type in ['cannon', 'ice'] and tower.target:
                pygame.draw.line(screen, YELLOW, tower.rect.center, tower.target.rect.center, 2)
            elif tower.type == 'flamethrower':
                pygame.draw.circle(screen, RED, tower.rect.center, tower.range, 1)

    # Draw slow effect on enemies
    for enemy in enemy_group:
        if enemy.slow_timer > 0:
            pygame.draw.circle(screen, BLUE, enemy.rect.center, enemy.rect.width // 2 + 5, 2)

    # UI
    resources_text = font.render(f"Resources: {resources}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    wave_text = font.render(f"Wave: {wave_number}", True, WHITE)
    screen.blit(resources_text, (10, 10))
    screen.blit(lives_text, (10, 50))
    screen.blit(wave_text, (10, 90))

    # Tower selection UI
    pygame.draw.rect(screen, BLUE, (10, 100, 50, 30))    # Cannon
    pygame.draw.rect(screen, RED, (70, 100, 50, 30))     # Flamethrower
    pygame.draw.rect(screen, WHITE, (130, 100, 50, 30))  # Ice
    pygame.draw.rect(screen, YELLOW, (190, 100, 50, 30)) # Generator

    # Hover info for tower stats
    pos = pygame.mouse.get_pos()
    if 10 <= pos[0] <= 60 and 100 <= pos[1] <= 130:
        text = font.render(f"Cannon: {tower_costs['cannon']} dmg:20 cd:60", True, WHITE)
        screen.blit(text, (10, 140))
    elif 70 <= pos[0] <= 120 and 100 <= pos[1] <= 130:
        text = font.render(f"Flamethrower: {tower_costs['flamethrower']} dmg:10 cd:30", True, WHITE)
        screen.blit(text, (70, 140))
    elif 130 <= pos[0] <= 180 and 100 <= pos[1] <= 130:
        text = font.render(f"Ice: {tower_costs['ice']} dmg:5 cd:45", True, WHITE)
        screen.blit(text, (130, 140))
    elif 190 <= pos[0] <= 240 and 100 <= pos[1] <= 130:
        text = font.render(f"Generator: {tower_costs['generator']} income:5/s", True, WHITE)
        screen.blit(text, (190, 140))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()