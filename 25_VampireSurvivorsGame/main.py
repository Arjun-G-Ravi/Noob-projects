import pygame
import random
from pygame.math import Vector2

# Initialize Pygame
pygame.init()

# Screen setup
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Vampire Survivors Clone")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
items = pygame.sprite.Group()

# Screen rectangle for boundary checking
screen_rect = screen.get_rect()

### Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(screen_width / 2, screen_height / 2))
        self.pos = Vector2(self.rect.center)
        self.speed = 300  # pixels per second
        self.health = 100
        self.experience = 0
        self.level = 1
        self.exp_to_next_level = 100
        self.weapons = [Weapon(self)]
        self.invincible_timer = 0

    def update(self, dt):
        # Movement
        keys = pygame.key.get_pressed()
        velocity = Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]: velocity.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: velocity.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: velocity.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: velocity.x += 1
        if velocity.length() > 0:
            velocity = velocity.normalize() * self.speed
        self.pos += velocity * dt
        self.rect.center = self.pos
        self.rect.clamp_ip(screen_rect)

        # Invincibility timer
        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        # Update weapons
        for weapon in self.weapons:
            weapon.update(dt)

### Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)
        self.speed = 100  # pixels per second
        self.health = 10

    def update(self, dt):
        direction = (player.pos - self.pos).normalize()
        self.pos += direction * self.speed * dt
        self.rect.center = self.pos

### Projectile Class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)
        self.velocity = direction * 500  # pixels per second
        self.damage = 5
        self.lifetime = 2.0  # seconds

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = self.pos
        self.lifetime -= dt
        if self.lifetime <= 0 or not screen_rect.contains(self.rect):
            self.kill()

### Item Class
class Item(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=pos)
        self.value = 10  # experience points

### Weapon Class
class Weapon:
    def __init__(self, player):
        self.player = player
        self.cooldown = 1.0  # seconds
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.cooldown:
            self.fire()
            self.timer = 0

    def fire(self):
        nearest_enemy = find_nearest_enemy(self.player.pos)
        if nearest_enemy:
            direction = (nearest_enemy.pos - self.player.pos).normalize()
            projectile = Projectile(self.player.pos, direction)
            all_sprites.add(projectile)
            projectiles.add(projectile)

### Utility Function
def find_nearest_enemy(position):
    nearest = None
    min_dist = float('inf')
    for enemy in enemies:
        dist = (enemy.pos - position).length()
        if dist < min_dist:
            min_dist = dist
            nearest = enemy
    return nearest

# Instantiate player
player = Player()
all_sprites.add(player)

# Enemy spawning setup
spawn_timer = 0
spawn_interval = 2.0  # seconds

# Main game loop
running = True
while running:
    dt = clock.tick(60) / 1000.0  # Delta time in seconds

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update all sprites
    all_sprites.update(dt)

    # Spawn enemies
    spawn_timer += dt
    if spawn_timer >= spawn_interval:
        spawn_timer = 0
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            pos = (random.randint(0, screen_width), -20)
        elif side == 'bottom':
            pos = (random.randint(0, screen_width), screen_height + 20)
        elif side == 'left':
            pos = (-20, random.randint(0, screen_height))
        else:  # right
            pos = (screen_width + 20, random.randint(0, screen_height))
        enemy = Enemy(pos)
        all_sprites.add(enemy)
        enemies.add(enemy)

    # Collision detection
    # Projectiles vs Enemies
    hits = pygame.sprite.groupcollide(projectiles, enemies, True, False)
    for projectile, enemies_hit in hits.items():
        for enemy in enemies_hit:
            enemy.health -= projectile.damage
            if enemy.health <= 0:
                enemy.kill()
                item = Item(enemy.rect.center)
                all_sprites.add(item)
                items.add(item)

    # Player vs Items
    hits = pygame.sprite.spritecollide(player, items, True)
    for item in hits:
        player.experience += item.value
        if player.experience >= player.exp_to_next_level:
            player.level += 1
            player.experience = 0
            # Upgrade weapon (reduce cooldown)
            for weapon in player.weapons:
                weapon.cooldown = max(0.1, weapon.cooldown * 0.9)

    # Player vs Enemies
    if player.invincible_timer <= 0:
        hits = pygame.sprite.spritecollide(player, enemies, False)
        if hits:
            player.health -= 10
            player.invincible_timer = 0.5  # 0.5-second invincibility

    # Drawing
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # UI: Health bar
    pygame.draw.rect(screen, RED, (10, 10, max(0, player.health * 2), 20))
    # UI: Experience bar
    exp_ratio = player.experience / player.exp_to_next_level
    pygame.draw.rect(screen, BLUE, (10, 40, exp_ratio * 200, 10))

    pygame.display.flip()

    # Game over condition
    if player.health <= 0:
        running = False

pygame.quit()