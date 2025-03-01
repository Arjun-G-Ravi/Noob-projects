import pygame
import random
import math
from pygame.math import Vector2
from upgrades import upgrade_gun, upgrade_blob, upgrade_heavy

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
GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)

# Font setup
font = pygame.font.SysFont(None, 22)

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
items = pygame.sprite.Group()

# Screen rectangle for boundary checking
screen_rect = screen.get_rect()

# Drop probabilities (modifiable)
DROP_PROBABILITIES = {
    "experience": 0.7,  # 70% chance
    "health": 0.05      # 30% chance
}

### Player Class (unchanged)
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
        self.exp_to_next_level = self.level
        self.weapons = [Gun(self), BlobWeapon(self), HeavyAttack(self)]
        self.invincible_timer = 0

    def update(self, dt):
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

        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        for weapon in self.weapons:
            weapon.update(dt)

### Enemy Classes
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, enemy_type="normal"):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = pygame.Surface((20, 20))
        if enemy_type == "normal":
            self.image.fill(GREEN)
            self.speed = 70
            self.health = 10
        elif enemy_type == "fast":
            self.image.fill(RED)
            self.speed = 200
            self.health = 10
        elif enemy_type == "strong":
            self.image.fill(BLUE)
            self.speed = 50
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
        self.piercing = piercing
        self.hit_enemies = set()

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
        self.hit_enemies = set()

    def update(self, dt):
        self.angle += self.rotation_speed * dt
        self.pos = Vector2(
            player.pos.x + math.cos(self.angle) * self.distance,
            player.pos.y + math.sin(self.angle) * self.distance
        )
        self.rect.center = self.pos

### Item Classes
class ExpItem(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=pos)
        self.value = 1

class HealthItem(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=pos)
        self.value = 10

### Weapon Classes
class Gun:
    def __init__(self, player):
        self.name = 'Gun'
        self.player = player
        self.level = 1
        self.damage = upgrade_gun[self.level]["damage"]
        self.cooldown = upgrade_gun[self.level]["cooldown"]
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
            projectile = Projectile(self.player.pos, direction, self.damage, RED, piercing=False)
            all_sprites.add(projectile)
            projectiles.add(projectile)

    def upgrade(self):
        if self.level < 10:
            self.level += 1
            self.damage = upgrade_gun[self.level]["damage"]
            self.cooldown = upgrade_gun[self.level]["cooldown"]

    def stats(self):
        return f"Gun (Lvl {self.level}/10): Dmg {self.damage}, CD {self.cooldown:.2f}s"

    def stats_next_level(self):
        if self.level < 10:
            next_level = self.level + 1
            dmg_diff = upgrade_gun[next_level]["damage"] - self.damage
            return f"Gun (Lvl {next_level}/10): Dmg {upgrade_gun[next_level]['damage']} (+{dmg_diff}), CD {upgrade_gun[next_level]['cooldown']:.2f}s"
        return f"Gun (Maxed): Dmg {self.damage}, CD {self.cooldown:.2f}s"

class BlobWeapon:
    def __init__(self, player):
        self.name = "Blob"
        self.player = player
        self.level = 1
        self.damage = upgrade_blob[self.level]["damage"]
        self.speed = upgrade_blob[self.level]["speed"]
        self.cooldown = 0.5
        self.timer = 0
        self.blob = None

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.cooldown:
            self.fire()
            self.timer = 0
        if self.blob:
            self.blob.update(dt)

    def fire(self):
        if self.blob and self.blob.alive():
            self.blob.damage = self.damage
            self.blob.rotation_speed = self.speed
        else:
            self.blob = Blob(self.player.pos, self.damage, self.speed)
            all_sprites.add(self.blob)
            projectiles.add(self.blob)

    def upgrade(self):
        if self.level < 10:
            self.level += 1
            self.damage = upgrade_blob[self.level]["damage"]
            self.speed = upgrade_blob[self.level]["speed"]
            if self.blob and self.blob.alive():
                self.blob.damage = self.damage
                self.blob.rotation_speed = self.speed

    def stats(self):
        return f"Blob (Lvl {self.level}/10): Dmg {self.damage}, Spd {self.speed:.1f}"

    def stats_next_level(self):
        if self.level < 10:
            next_level = self.level + 1
            dmg_diff = upgrade_blob[next_level]["damage"] - self.damage
            spd_diff = upgrade_blob[next_level]["speed"] - self.speed
            return f"Blob (Lvl {next_level}/10): Dmg {upgrade_blob[next_level]['damage']} (+{dmg_diff}), Spd {upgrade_blob[next_level]['speed']:.1f} (+{spd_diff:.1f})"
        return f"Blob (Maxed): Dmg {self.damage}, Spd {self.speed:.1f}"

class HeavyAttack:
    def __init__(self, player):
        self.name = 'Heavy'
        self.player = player
        self.level = 1
        self.damage = upgrade_heavy[self.level]["damage"]
        self.cooldown = upgrade_heavy[self.level]["cooldown"]
        self.timer = self.cooldown
        self.beam_count = 12
        self.ready = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if not self.ready:
            self.timer += dt
            if self.timer >= self.cooldown:
                self.ready = True
                self.timer = self.cooldown
        if keys[pygame.K_SPACE] and self.ready:
            self.fire()
            self.ready = False
            self.timer = 0

    def fire(self):
        angle_step = 360 / self.beam_count
        for i in range(self.beam_count):
            angle = math.radians(i * angle_step)
            direction = Vector2(math.cos(angle), math.sin(angle)).normalize()
            projectile = Projectile(self.player.pos, direction, self.damage, BLUE, piercing=True)
            all_sprites.add(projectile)
            projectiles.add(projectile)

    def upgrade(self):
        if self.level < 10:
            self.level += 1
            self.damage = upgrade_heavy[self.level]["damage"]
            self.cooldown = upgrade_heavy[self.level]["cooldown"]

    def stats(self):
        reload = self.cooldown - self.timer if not self.ready else 0
        return f"Heavy (Lvl {self.level}/10): Dmg {self.damage}, Rld {reload:.1f}s"

    def stats_next_level(self):
        if self.level < 10:
            next_level = self.level + 1
            dmg_diff = upgrade_heavy[next_level]["damage"] - self.damage
            reload = upgrade_heavy[next_level]["cooldown"] - self.timer if not self.ready else 0
            return f"Heavy (Lvl {next_level}/10): Dmg {upgrade_heavy[next_level]['damage']} (+{dmg_diff}), Rld {reload:.1f}s"
        reload = self.cooldown - self.timer if not self.ready else 0
        return f"Heavy (Maxed): Dmg {self.damage}, Rld {reload:.1f}s"

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
base_spawn_interval = 3

# Game state
game_state = "playing"

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
            if game_state == "upgrading":
                if event.key == pygame.K_1 and player.weapons[0].level < 10:
                    player.weapons[0].upgrade()
                    game_state = "playing"
                elif event.key == pygame.K_2 and player.weapons[1].level < 10:
                    player.weapons[1].upgrade()
                    game_state = "playing"
                elif event.key == pygame.K_3 and player.weapons[2].level < 10:
                    player.weapons[2].upgrade()
                    game_state = "playing"
        elif event.type == pygame.MOUSEBUTTONDOWN and game_state == "upgrading":
            mouse_pos = pygame.mouse.get_pos()
            # Check if clicked on upgrade buttons
            all_maxed = all(weapon.level >= 10 for weapon in player.weapons)
            if all_maxed:
                if upgrade_rects[0].collidepoint(mouse_pos):
                    player.health = 100
                    game_state = "playing"
            else:
                for i, rect in enumerate(upgrade_rects):
                    if rect.collidepoint(mouse_pos) and player.weapons[i].level < 10:
                        player.weapons[i].upgrade()
                        game_state = "playing"
                        break

    # Update game logic only when playing
    if game_state == "playing":
        all_sprites.update(dt)

        # Dynamic spawn interval based on player level
        spawn_interval = max(0.5, base_spawn_interval - 0.5 * (player.level - 1))
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
            else:
                pos = (screen_width + 20, random.randint(0, screen_height))
            enemy_type = random.choices(
                ["normal", "fast", "strong"],
                weights=[80, 15, 5],
                k=1
            )[0]
            enemy = Enemy(pos, enemy_type)
            all_sprites.add(enemy)
            enemies.add(enemy)

        # Collision detection (unchanged)
        for projectile in projectiles:
            if isinstance(projectile, Blob):
                hits = pygame.sprite.spritecollide(projectile, enemies, False)
                for enemy in hits:
                    if enemy not in projectile.hit_enemies:
                        enemy.health -= projectile.damage
                        projectile.hit_enemies.add(enemy)
                        if enemy.health <= 0:
                            enemy.kill()
                            drop = random.choices(["experience", "health"], 
                                                weights=[DROP_PROBABILITIES["experience"], 
                                                        DROP_PROBABILITIES["health"]], 
                                                k=1)[0]
                            if drop == "experience":
                                item = ExpItem(enemy.rect.center)
                            else:
                                item = HealthItem(enemy.rect.center)
                            all_sprites.add(item)
                            items.add(item)
                if projectile.angle >= 2 * math.pi:
                    projectile.hit_enemies.clear()
                    projectile.angle -= 2 * math.pi
            else:
                hits = pygame.sprite.spritecollide(projectile, enemies, False)
                for enemy in hits:
                    if enemy not in projectile.hit_enemies:
                        enemy.health -= projectile.damage
                        projectile.hit_enemies.add(enemy)
                        if not projectile.piercing:
                            projectile.kill()
                        if enemy.health <= 0:
                            enemy.kill()
                            drop = random.choices(["experience", "health"], 
                                                weights=[DROP_PROBABILITIES["experience"], 
                                                        DROP_PROBABILITIES["health"]], 
                                                k=1)[0]
                            if drop == "experience":
                                item = ExpItem(enemy.rect.center)
                            else:
                                item = HealthItem(enemy.rect.center)
                            all_sprites.add(item)
                            items.add(item)
                        break

        # Player vs Items (unchanged)
        hits = pygame.sprite.spritecollide(player, items, True)
        for item in hits:
            if isinstance(item, ExpItem):
                player.experience += item.value
                if player.experience >= player.exp_to_next_level:
                    player.level += 1
                    player.experience -= player.exp_to_next_level
                    player.exp_to_next_level = player.level
                    game_state = "upgrading"
            elif isinstance(item, HealthItem):
                player.health = min(100, player.health + item.value)

        # Player vs Enemies (unchanged)
        if player.invincible_timer <= 0:
            hits = pygame.sprite.spritecollide(player, enemies, False)
            if hits:
                player.health -= 10
                player.invincible_timer = 0.5

    # Drawing
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Draw upgrade menu when upgrading
    if game_state == "upgrading":
        upgrade_rects = []
        all_maxed = all(weapon.level >= 10 for weapon in player.weapons)
        
        # Background
        pygame.draw.rect(screen, GRAY, (100, 200, 600, 200))
        title_text = font.render("Level Up! Choose an upgrade:", True, WHITE)
        screen.blit(title_text, (screen_width//2 - title_text.get_width()//2, 220))

        if all_maxed:
            # Only show health restore option
            text = font.render("All weapons maxed! Restore Health to Full", True, WHITE)
            text_rect = text.get_rect(center=(screen_width//2, 300))
            upgrade_rects.append(pygame.Rect(text_rect.left - 10, text_rect.top - 10, 
                                          text_rect.width + 20, text_rect.height + 20))
            pygame.draw.rect(screen, LIGHT_GRAY, upgrade_rects[0])
            screen.blit(text, text_rect)
        else:
            # Horizontal weapon selection
            button_width = 180
            total_width = button_width * len(player.weapons)
            start_x = (screen_width - total_width - 20 * (len(player.weapons) - 1)) // 2
            
            for i, weapon in enumerate(player.weapons):
                x = start_x + i * (button_width + 20)
                if weapon.level >= 10:
                    upgrade_text = font.render(f"{weapon.stats()} - MAXED OUT", True, WHITE)
                else:
                    upgrade_text1 = font.render(f"{weapon.name}: Lv {weapon.level}", True, WHITE)
                    upgrade_text2 = font.render(f"Damage: {weapon.damage}", True, WHITE)
                    upgrade_text3 = font.render(f"Cooldown: {weapon.cooldown}", True, WHITE)
                
                text_rect = upgrade_text1.get_rect(center=(x + button_width//2, 300))
                text_rect = upgrade_text2.get_rect(center=(x + button_width//2, 300))
                text_rect = upgrade_text3.get_rect(center=(x + button_width//2, 300))
                button_rect = pygame.Rect(x, 280, button_width, 80)
                upgrade_rects.append(button_rect)
                
                # Draw button
                pygame.draw.rect(screen, LIGHT_GRAY if weapon.level < 10 else GRAY, button_rect)
                screen.blit(upgrade_text, text_rect)

    # UI: Top-left - Health and Level (unchanged)
    health_text = font.render(f"Health: {max(0, player.health)}", True, WHITE)
    level_text = font.render(f"Level: {player.level}", True, WHITE)
    screen.blit(health_text, (5, 5))
    screen.blit(level_text, (5, 30))
    exp_ratio = player.experience / player.exp_to_next_level if player.exp_to_next_level > 0 else 0
    pygame.draw.rect(screen, BLUE, (5, 55, exp_ratio * 150, 10))

    # UI: Top-right - Weapon Stats (unchanged)
    weapon_stats = [weapon.stats() for weapon in player.weapons]
    for i, stat in enumerate(weapon_stats):
        stat_text = font.render(stat, True, WHITE)
        screen.blit(stat_text, (screen_width - 250, 10 + i * 30))

    pygame.display.flip()

    # Game over condition
    if player.health <= 0:
        running = False

pygame.quit()