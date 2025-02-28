import pygame
import random
import math
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
YELLOW = (255, 255, 0)

# Font setup
font = pygame.font.SysFont(None, 28)

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
        self.speed = 300
        self.health = 100
        self.experience = 0
        self.level = 1
        self.exp_to_next_level = 100
        self.weapons = [Gun(self), BlobWeapon(self), HeavyAttack(self)]
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

### Enemy Classes
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, enemy_type="normal"):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = pygame.Surface((20, 20))
        
        # Set properties based on enemy type
        if enemy_type == "normal":
            self.image.fill(GREEN)
            self.speed = 100
            self.health = 10
        elif enemy_type == "fast":
            self.image.fill(RED)
            self.speed = 500
            self.health = 10
        elif enemy_type == "strong":
            self.image.fill(BLUE)
            self.speed = 100
            self.health = 100
            
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)

    def update(self, dt):
        direction = (player.pos - self.pos).normalize()
        self.pos += direction * self.speed * dt
        self.rect.center = self.pos

### Projectile Class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, damage, color=RED, piercing=False):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)
        self.velocity = direction * 500
        self.damage = damage
        self.lifetime = 2.0
        self.piercing = piercing  # Whether it passes through enemies

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = self.pos
        self.lifetime -= dt
        if self.lifetime <= 0 or not screen_rect.contains(self.rect):
            self.kill()

### Blob Class (Rotating Projectile)
class Blob(pygame.sprite.Sprite):
    def __init__(self, pos, damage, speed):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)
        self.damage = damage
        self.rotation_speed = speed
        self.angle = 0
        self.distance = 100
        self.reset_pos = pos

    def update(self, dt):
        self.angle += self.rotation_speed * dt
        self.pos = Vector2(
            player.pos.x + math.cos(self.angle) * self.distance,
            player.pos.y + math.sin(self.angle) * self.distance
        )
        self.rect.center = self.pos

    def collide(self):
        self.pos = Vector2(self.reset_pos)  # Reset to initial position
        self.rect.center = self.pos
        self.angle = 0

### Item Class
class Item(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=pos)
        self.value = 10

### Weapon Classes
class Gun:
    def __init__(self, player):
        self.player = player
        self.cooldown = 1.0
        self.timer = 0
        self.base_damage = 5

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.cooldown:
            self.fire()
            self.timer = 0

    def fire(self):
        nearest_enemy = find_nearest_enemy(self.player.pos)
        if nearest_enemy:
            direction = (nearest_enemy.pos - self.player.pos).normalize()
            damage = self.base_damage + self.player.level * 2
            projectile = Projectile(self.player.pos, direction, damage)
            all_sprites.add(projectile)
            projectiles.add(projectile)

    def stats(self):
        damage = self.base_damage + self.player.level * 2
        return f"Gun: Dmg {damage}, CD {self.cooldown:.1f}s"

class BlobWeapon:
    def __init__(self, player):
        self.player = player
        self.cooldown = 0.5
        self.timer = 0
        self.base_damage = 3
        self.base_speed = 0.5
        self.blob = None

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.cooldown:
            self.fire()
            self.timer = 0
        if self.blob:
            self.blob.update(dt)

    def fire(self):
        if not self.blob or not self.blob.alive():
            damage = self.base_damage + self.player.level
            speed = self.base_speed + self.player.level * 0.5
            self.blob = Blob(self.player.pos, damage, speed)
            all_sprites.add(self.blob)
            projectiles.add(self.blob)

    def stats(self):
        damage = self.base_damage + self.player.level
        speed = self.base_speed + self.player.level * 0.5
        return f"Blob: Dmg {damage}, Spd {speed:.1f}"

class HeavyAttack:
    def __init__(self, player):
        self.player = player
        self.cooldown = 30.0  # 30-second cooldown
        self.timer = self.cooldown  # Start ready to fire
        self.base_damage = 20
        self.beam_count = 12
        self.ready = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if not self.ready:
            self.timer += dt
            if self.timer >= self.cooldown:
                self.ready = True
                self.timer = self.cooldown  # Cap the timer at cooldown
        if keys[pygame.K_SPACE] and self.ready:
            self.fire()
            self.ready = False
            self.timer = 0

    def fire(self):
        damage = self.base_damage + self.player.level * 5
        angle_step = 360 / self.beam_count
        for i in range(self.beam_count):
            angle = math.radians(i * angle_step)
            direction = Vector2(math.cos(angle), math.sin(angle)).normalize()
            projectile = Projectile(self.player.pos, direction, damage, BLUE, piercing=True)
            all_sprites.add(projectile)
            projectiles.add(projectile)

    def stats(self):
        damage = self.base_damage + self.player.level * 5
        reload = self.cooldown - self.timer if not self.ready else 0
        return f"Heavy: Dmg {damage}, Rld {reload:.1f}s"

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
spawn_interval = 1.0

# Main game loop
running = True
while running:
    dt = clock.tick(60) / 1000.0

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
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
        enemy_type = random.choices(
            ["normal", "fast", "strong"],
            weights=[60, 20, 20],  # 60% normal, 20% fast, 20% strong
            k=1
        )[0]
        enemy = Enemy(pos, enemy_type)
        all_sprites.add(enemy)
        enemies.add(enemy)

    # Collision detection
    # Projectiles vs Enemies
    for projectile in projectiles:
        if isinstance(projectile, Blob):
            hits = pygame.sprite.spritecollide(projectile, enemies, False)
            for enemy in hits:
                enemy.health -= projectile.damage
                projectile.collide()  # Reset position on hit
                if enemy.health <= 0:
                    enemy.kill()
                    item = Item(enemy.rect.center)
                    all_sprites.add(item)
                    items.add(item)
        else:
            hits = pygame.sprite.spritecollide(projectile, enemies, not projectile.piercing)
            for enemy in hits:
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
            for weapon in player.weapons:
                if isinstance(weapon, Gun):
                    weapon.cooldown = max(0.1, weapon.cooldown * 0.9)
                elif isinstance(weapon, HeavyAttack):
                    weapon.cooldown = max(15.0, weapon.cooldown * 0.9)

    # Player vs Enemies
    if player.invincible_timer <= 0:
        hits = pygame.sprite.spritecollide(player, enemies, False)
        if hits:
            player.health -= 10
            player.invincible_timer = 0.5

    # Drawing
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # UI: Top-left - Health and Level
    health_text = font.render(f"Health: {max(0, player.health)}", True, WHITE)
    level_text = font.render(f"Level: {player.level}", True, WHITE)
    screen.blit(health_text, (10, 10))
    screen.blit(level_text, (10, 40))
    exp_ratio = player.experience / player.exp_to_next_level
    pygame.draw.rect(screen, BLUE, (10, 70, exp_ratio * 200, 10))

    # UI: Top-right - Weapon Stats
    weapon_stats = [weapon.stats() for weapon in player.weapons]
    for i, stat in enumerate(weapon_stats):
        stat_text = font.render(stat, True, WHITE)
        screen.blit(stat_text, (screen_width - 250, 10 + i * 30))

    pygame.display.flip()

    # Game over condition
    if player.health <= 0:
        running = False

pygame.quit()